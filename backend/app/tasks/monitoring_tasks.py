from celery import current_task
from app.core.celery_app import celery_app
from app.db.database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import text, func, and_, or_
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
import json
import requests
from collections import defaultdict

logger = logging.getLogger(__name__)

class PipelineMonitor:
    def __init__(self):
        self.alert_thresholds = {
            'scraping_failure_rate': 0.2,  # 20% failure rate
            'processing_failure_rate': 0.15,  # 15% failure rate
            'data_quality_score': 60,  # Minimum quality score
            'pipeline_downtime': 3600,  # 1 hour in seconds
            'critical_event_threshold': 10  # 10+ fatalities
        }

    def check_scraping_health(self, db: Session) -> Dict[str, Any]:
        """Check health of scraping tasks"""
        try:
            # Since we don't have a task_results table, we'll monitor data freshness instead
            query = text("""
                SELECT 
                    COUNT(*) as total_events,
                    COUNT(CASE WHEN fatalities > 0 THEN 1 END) as events_with_fatalities,
                    MAX(created_at) as last_update,
                    MAX(event_date) as latest_event,
                    COUNT(DISTINCT state) as affected_states,
                    AVG(fatalities) as avg_fatalities
                FROM conflict_events 
                WHERE created_at >= NOW() - INTERVAL '24 hours'
            """)
            
            result = db.execute(query).fetchone()
            
            if not result or result.total_events == 0:
                return {
                    'overall_status': 'unhealthy',
                    'message': 'No recent data found',
                    'total_events': 0,
                    'last_update': None
                }
            
            # Calculate health based on data freshness and volume
            hours_since_last_update = (datetime.utcnow() - result.last_update).total_seconds() / 3600 if result.last_update else 999
            
            health_status = {
                'overall_status': 'healthy' if hours_since_last_update < 6 else 'unhealthy',
                'total_events': result.total_events,
                'events_with_fatalities': result.events_with_fatalities,
                'last_update': result.last_update,
                'latest_event': result.latest_event,
                'affected_states': result.affected_states,
                'avg_fatalities': result.avg_fatalities or 0,
                'hours_since_last_update': hours_since_last_update,
                'message': f'Data updated {hours_since_last_update:.1f} hours ago'
            }
            
            return health_status
            
        except Exception as e:
            logger.error(f"Error checking scraping health: {str(e)}")
            return {'status': 'error', 'error': str(e)}

    def check_data_quality(self, db: Session) -> Dict[str, Any]:
        """Check quality of processed data"""
        try:
            # Query actual data quality metrics from conflict_events table
            query = text("""
                SELECT 
                    COUNT(*) as total_events,
                    COUNT(CASE WHEN fatalities > 0 THEN 1 END) as events_with_fatalities,
                    COUNT(CASE WHEN latitude IS NOT NULL AND longitude IS NOT NULL THEN 1 END) as events_with_coordinates,
                    COUNT(CASE WHEN verified = true THEN 1 END) as verified_events,
                    COUNT(DISTINCT state) as unique_states,
                    COUNT(DISTINCT event_type) as unique_event_types,
                    MAX(event_date) as latest_event,
                    AVG(CASE WHEN fatalities > 0 THEN fatalities END) as avg_fatalities_when_fatal,
                    SUM(fatalities) as total_fatalities
                FROM conflict_events
                WHERE event_date >= CURRENT_DATE - INTERVAL '30 days'
            """)
            
            result = db.execute(query).fetchone()
            
            if not result or result.total_events == 0:
                return {
                    'status': 'unhealthy',
                    'quality_score': 0,
                    'message': 'No data found in last 30 days'
                }
            
            # Calculate quality metrics
            verification_rate = (result.verified_events / result.total_events) if result.total_events > 0 else 0
            geocoding_rate = (result.events_with_coordinates / result.total_events) if result.total_events > 0 else 0
            fatality_rate = (result.events_with_fatalities / result.total_events) if result.total_events > 0 else 0
            
            # Quality score based on multiple factors
            quality_score = (
                verification_rate * 40 +  # 40% weight for verification
                geocoding_rate * 30 +     # 30% weight for geocoding
                min(fatality_rate * 2, 30)  # 30% weight for fatality reporting (capped)
            )
            
            return {
                'status': 'healthy' if quality_score >= 60 else 'unhealthy',
                'quality_score': quality_score,
                'verification_rate': verification_rate,
                'geocoding_rate': geocoding_rate,
                'fatality_rate': fatality_rate,
                'avg_fatalities_when_fatal': result.avg_fatalities_when_fatal or 0,
                'total_events': result.total_events,
                'events_with_fatalities': result.events_with_fatalities,
                'unique_states': result.unique_states,
                'unique_event_types': result.unique_event_types,
                'latest_event': result.latest_event,
                'total_fatalities': result.total_fatalities,
                'message': f'Quality score: {quality_score:.1f}%'
            }
            
        except Exception as e:
            logger.error(f"Error checking data quality: {str(e)}")
            return {'status': 'error', 'error': str(e)}

    def detect_anomalies(self, db: Session) -> List[Dict[str, Any]]:
        """Detect anomalies in conflict data"""
        try:
            anomalies = []
            
            # Detect fatality spikes (events with unusually high fatalities)
            spike_query = text("""
                SELECT state, event_date, fatalities, event_type
                FROM conflict_events 
                WHERE fatalities > 10 
                AND event_date >= CURRENT_DATE - INTERVAL '7 days'
                ORDER BY fatalities DESC
                LIMIT 5
            """)
            
            spike_results = db.execute(spike_query).fetchall()
            for row in spike_results:
                anomalies.append({
                    'type': 'fatality_spike',
                    'severity': 'high' if row.fatalities > 20 else 'medium',
                    'description': f'High fatality event in {row.state}: {row.fatalities} fatalities',
                    'location': row.state,
                    'date': row.event_date.isoformat() if row.event_date else None,
                    'event_type': row.event_type,
                    'fatalities': row.fatalities,
                    'timestamp': datetime.utcnow().isoformat()
                })
            
            # Detect data gaps (states with no recent data)
            gap_query = text("""
                SELECT s.name as state_name
                FROM states s
                LEFT JOIN conflict_events ce ON s.name = ce.state 
                    AND ce.event_date >= CURRENT_DATE - INTERVAL '7 days'
                WHERE ce.id IS NULL
                LIMIT 10
            """)
            
            gap_results = db.execute(gap_query).fetchall()
            for row in gap_results:
                anomalies.append({
                    'type': 'data_gap',
                    'severity': 'medium',
                    'description': f'No recent conflict data from {row.state_name}',
                    'location': row.state_name,
                    'timestamp': datetime.utcnow().isoformat()
                })
            
            # Detect unusual patterns (high frequency of events in a state)
            pattern_query = text("""
                SELECT state, COUNT(*) as event_count
                FROM conflict_events 
                WHERE event_date >= CURRENT_DATE - INTERVAL '24 hours'
                GROUP BY state
                HAVING COUNT(*) > 5
                ORDER BY event_count DESC
            """)
            
            pattern_results = db.execute(pattern_query).fetchall()
            for row in pattern_results:
                anomalies.append({
                    'type': 'high_frequency',
                    'severity': 'medium',
                    'description': f'High frequency of events in {row.state}: {row.event_count} events in 24h',
                    'location': row.state,
                    'event_count': row.event_count,
                    'timestamp': datetime.utcnow().isoformat()
                })
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {str(e)}")
            return [{
                'type': 'detection_error',
                'severity': 'low',
                'description': f'Anomaly detection failed: {str(e)}',
                'timestamp': datetime.utcnow().isoformat()
            }]

    def generate_alerts(self, health_data: Dict[str, Any], quality_data: Dict[str, Any], anomalies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate alerts based on monitoring data"""
        alerts = []
        
        # Health alerts
        if health_data.get('overall_status') == 'unhealthy':
            alerts.append({
                'type': 'health',
                'severity': 'high',
                'title': 'Pipeline Health Issues',
                'message': f"{health_data['failed_sources']} sources are failing",
                'timestamp': datetime.utcnow().isoformat()
            })
        
        # Quality alerts
        if quality_data.get('quality_score', 100) < self.alert_thresholds['data_quality_score']:
            alerts.append({
                'type': 'quality',
                'severity': 'medium',
                'title': 'Data Quality Degradation',
                'message': f"Quality score: {quality_data.get('quality_score', 0):.1f}",
                'timestamp': datetime.utcnow().isoformat()
            })
        
        # Anomaly alerts
        for anomaly in anomalies:
            if anomaly['severity'] == 'high':
                alerts.append({
                    'type': 'anomaly',
                    'severity': 'high',
                    'title': 'Critical Anomaly Detected',
                    'message': anomaly['description'],
                    'timestamp': datetime.utcnow().isoformat(),
                    'details': anomaly
                })
        
        return alerts

@celery_app.task(bind=True, name='app.tasks.monitoring_tasks.check_pipeline_health')
def check_pipeline_health(self):
    """Comprehensive pipeline health check"""
    try:
        monitor = PipelineMonitor()
        db = next(get_db())
        
        # Update initial status
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Starting pipeline health check'}
        )
        
        # Check different aspects
        scraping_health = monitor.check_scraping_health(db)
        data_quality = monitor.check_data_quality(db)
        anomalies = monitor.detect_anomalies(db)
        
        # Generate alerts
        alerts = monitor.generate_alerts(scraping_health, data_quality, anomalies)
        
        # Store monitoring results
        monitoring_result = {
            'timestamp': datetime.utcnow().isoformat(),
            'scraping_health': scraping_health,
            'data_quality': data_quality,
            'anomalies': anomalies,
            'alerts': alerts,
            'overall_status': 'healthy' if not alerts else 'alert'
        }
        
        # Store in database (would implement monitoring table)
        # store_monitoring_result(monitoring_result)
        
        # Send alerts if any
        if alerts:
            send_alerts.delay(alerts)
        
        # Update final status
        self.update_state(
            state='SUCCESS',
            meta={
                'status': 'Pipeline health check completed',
                'alerts_generated': len(alerts),
                'anomalies_detected': len(anomalies)
            }
        )
        
        logger.info(f"Pipeline health check completed: {len(alerts)} alerts, {len(anomalies)} anomalies")
        
        return monitoring_result
        
    except Exception as e:
        logger.error(f"Error in check_pipeline_health task: {str(e)}")
        self.update_state(
            state='FAILURE',
            meta={'error': str(e)}
        )
        raise
    finally:
        db.close()

@celery_app.task(bind=True, name='app.tasks.monitoring_tasks.send_alerts')
def send_alerts(self, alerts: List[Dict[str, Any]]):
    """Send alerts via various channels"""
    try:
        for alert in alerts:
            # Log alert
            logger.warning(f"ALERT: {alert['title']} - {alert['message']}")
            
            # Send email alert (would implement email service)
            # send_email_alert(alert)
            
            # Send Slack notification (would implement Slack integration)
            # send_slack_alert(alert)
            
            # Send SMS for critical alerts (would implement SMS service)
            if alert['severity'] == 'high':
                # send_sms_alert(alert)
                pass
        
        return {
            'sent_at': datetime.utcnow().isoformat(),
            'alerts_sent': len(alerts)
        }
        
    except Exception as e:
        logger.error(f"Error sending alerts: {str(e)}")
        raise

@celery_app.task(bind=True, name='app.tasks.monitoring_tasks.generate_daily_report')
def generate_daily_report(self):
    """Generate daily conflict monitoring report"""
    try:
        db = next(get_db())
        
        # Get daily statistics
        stats_query = text("""
            SELECT 
                DATE(event_date) as report_date,
                COUNT(*) as total_conflicts,
                SUM(fatalities) as total_fatalities,
                SUM(injuries) as total_injuries,
                COUNT(DISTINCT state) as affected_states,
                COUNT(DISTINCT event_type) as event_types,
                COUNT(DISTINCT source) as sources
            FROM conflict_events
            WHERE event_date >= CURRENT_DATE - INTERVAL '1 day'
            GROUP BY DATE(event_date)
            ORDER BY report_date DESC
        """)
        
        results = db.execute(stats_query).fetchall()
        
        if not results:
            return {
                'generated_at': datetime.utcnow().isoformat(),
                'message': 'No data available for daily report'
            }
        
        # Get top affected states
        states_query = text("""
            SELECT 
                state,
                COUNT(*) as conflict_count,
                SUM(fatalities) as fatalities
            FROM conflict_events
            WHERE event_date >= CURRENT_DATE - INTERVAL '1 day'
            GROUP BY state
            ORDER BY conflict_count DESC
            LIMIT 10
        """)
        
        top_states = db.execute(states_query).fetchall()
        
        # Get event type breakdown
        events_query = text("""
            SELECT 
                event_type,
                COUNT(*) as count,
                SUM(fatalities) as fatalities
            FROM conflict_events
            WHERE event_date >= CURRENT_DATE - INTERVAL '1 day'
            GROUP BY event_type
            ORDER BY count DESC
        """)
        
        event_breakdown = db.execute(events_query).fetchall()
        
        # Compile report
        report = {
            'generated_at': datetime.utcnow().isoformat(),
            'report_date': results[0].report_date.isoformat(),
            'summary': {
                'total_conflicts': results[0].total_conflicts,
                'total_fatalities': results[0].total_fatalities,
                'total_injuries': results[0].total_injuries,
                'affected_states': results[0].affected_states,
                'event_types': results[0].event_types,
                'sources': results[0].sources
            },
            'top_affected_states': [
                {
                    'state': row.state,
                    'conflicts': row.conflict_count,
                    'fatalities': row.fatalities
                }
                for row in top_states
            ],
            'event_breakdown': [
                {
                    'type': row.event_type,
                    'count': row.count,
                    'fatalities': row.fatalities
                }
                for row in event_breakdown
            ]
        }
        
        logger.info(f"Daily report generated: {report['summary']['total_conflicts']} conflicts")
        
        return report
        
    except Exception as e:
        logger.error(f"Error generating daily report: {str(e)}")
        raise
    finally:
        db.close()

@celery_app.task(bind=True, name='app.tasks.monitoring_tasks.check_data_freshness')
def check_data_freshness(self):
    """Check if data is being updated regularly"""
    try:
        db = next(get_db())
        
        # Check latest data timestamp
        query = text("""
            SELECT 
                MAX(created_at) as latest_update,
                MAX(event_date) as latest_event,
                COUNT(*) as events_today,
                COUNT(*) as events_this_week
            FROM conflict_events
            WHERE created_at >= CURRENT_DATE
        """)
        
        result = db.execute(query).fetchone()
        
        if not result or result.events_today == 0:
            return {
                'status': 'no_data',
                'message': 'No data found today'
            }
        
        # Check if data is stale (older than 6 hours)
        now = datetime.utcnow()
        latest_update = result.latest_update or datetime.min
        data_age_hours = (now - latest_update).total_seconds() / 3600
        
        is_stale = data_age_hours > 6
        
        return {
            'checked_at': now.isoformat(),
            'latest_update': latest_update.isoformat(),
            'latest_event': result.latest_event.isoformat() if result.latest_event else None,
            'events_today': result.events_today,
            'events_this_week': result.events_this_week,
            'data_age_hours': data_age_hours,
            'is_stale': is_stale,
            'status': 'stale' if is_stale else 'fresh',
            'message': f'Data is {"stale" if is_stale else "fresh"} ({data_age_hours:.1f}h old)'
        }
        
    except Exception as e:
        logger.error(f"Error checking data freshness: {str(e)}")
        raise
    finally:
        db.close()

@celery_app.task(bind=True, name='app.tasks.monitoring_tasks.monitor_system_resources')
def monitor_system_resources(self):
    """Monitor system resource usage"""
    try:
        import psutil
        
        # Get system metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Check Redis connection
        redis_status = 'healthy'
        try:
            from app.core.celery_app import celery_app
            inspect = celery_app.control.inspect()
            stats = inspect.stats()
            if not stats:
                redis_status = 'no_workers'
        except Exception as e:
            redis_status = 'error'
        
        metrics = {
            'timestamp': datetime.utcnow().isoformat(),
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'memory_available_gb': memory.available / (1024**3),
            'disk_percent': (disk.used / disk.total) * 100,
            'disk_free_gb': disk.free / (1024**3),
            'redis_status': redis_status,
            'worker_count': len(stats) if stats else 0
        }
        
        # Check for resource warnings
        warnings = []
        if cpu_percent > 80:
            warnings.append('High CPU usage')
        if memory.percent > 85:
            warnings.append('High memory usage')
        if (disk.used / disk.total) > 90:
            warnings.append('Low disk space')
        
        metrics['warnings'] = warnings
        metrics['status'] = 'warning' if warnings else 'healthy'
        
        return metrics
        
    except Exception as e:
        logger.error(f"Error monitoring system resources: {str(e)}")
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'error',
            'error': str(e)
        }
