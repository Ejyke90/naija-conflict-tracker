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
            # Get recent scraping tasks
            query = text("""
                SELECT 
                    source,
                    COUNT(*) as total_tasks,
                    COUNT(CASE WHEN status = 'SUCCESS' THEN 1 END) as successful_tasks,
                    COUNT(CASE WHEN status = 'FAILURE' THEN 1 END) as failed_tasks,
                    AVG(CASE WHEN status = 'SUCCESS' THEN execution_time END) as avg_execution_time,
                    MAX(created_at) as last_run
                FROM task_results 
                WHERE task_name LIKE '%scrape%'
                AND created_at >= NOW() - INTERVAL '24 hours'
                GROUP BY source
            """)
            
            results = db.execute(query).fetchall()
            
            health_status = {
                'overall_status': 'healthy',
                'sources': [],
                'total_sources': len(results),
                'failed_sources': 0,
                'avg_success_rate': 0
            }
            
            total_success_rate = 0
            
            for row in results:
                success_rate = (row.successful_tasks / row.total_tasks) if row.total_tasks > 0 else 0
                
                source_status = {
                    'source': row.source,
                    'status': 'healthy' if success_rate >= 0.8 else 'unhealthy',
                    'success_rate': success_rate,
                    'last_run': row.last_run,
                    'avg_execution_time': row.avg_execution_time
                }
                
                health_status['sources'].append(source_status)
                
                if success_rate < 0.8:
                    health_status['failed_sources'] += 1
                    health_status['overall_status'] = 'unhealthy'
                
                total_success_rate += success_rate
            
            if results:
                health_status['avg_success_rate'] = total_success_rate / len(results)
            
            return health_status
            
        except Exception as e:
            logger.error(f"Error checking scraping health: {str(e)}")
            return {'status': 'error', 'error': str(e)}

    def check_data_quality(self, db: Session) -> Dict[str, Any]:
        """Check quality of processed data"""
        try:
            query = text("""
                SELECT 
                    COUNT(*) as total_events,
                    COUNT(CASE WHEN verification_score >= 60 THEN 1 END) as verified_events,
                    AVG(verification_score) as avg_verification_score,
                    COUNT(CASE WHEN fatalities > 0 THEN 1 END) as events_with_fatalities,
                    COUNT(CASE WHEN coordinates IS NOT NULL THEN 1 END) as geocoded_events,
                    COUNT(DISTINCT source) as unique_sources,
                    MAX(date_occurred) as latest_event
                FROM conflicts 
                WHERE created_at >= NOW() - INTERVAL '24 hours'
            """)
            
            result = db.execute(query).fetchone()
            
            if not result:
                return {'status': 'no_data', 'message': 'No events found in last 24 hours'}
            
            verification_rate = (result.verified_events / result.total_events) if result.total_events > 0 else 0
            geocoding_rate = (result.geocoded_events / result.total_events) if result.total_events > 0 else 0
            
            quality_score = (
                (verification_rate * 40) + 
                (geocoding_rate * 30) + 
                (min(result.avg_verification_score / 100, 1) * 30)
            )
            
            status = 'excellent' if quality_score >= 90 else \
                    'good' if quality_score >= 75 else \
                    'fair' if quality_score >= 60 else 'poor'
            
            return {
                'status': status,
                'quality_score': quality_score,
                'total_events': result.total_events,
                'verification_rate': verification_rate,
                'geocoding_rate': geocoding_rate,
                'avg_verification_score': result.avg_verification_score,
                'events_with_fatalities': result.events_with_fatalities,
                'unique_sources': result.unique_sources,
                'latest_event': result.latest_event
            }
            
        except Exception as e:
            logger.error(f"Error checking data quality: {str(e)}")
            return {'status': 'error', 'error': str(e)}

    def detect_anomalies(self, db: Session) -> List[Dict[str, Any]]:
        """Detect anomalies in conflict data"""
        try:
            anomalies = []
            
            # Check for sudden spikes in conflicts
            spike_query = text("""
                WITH hourly_counts AS (
                    SELECT 
                        DATE_TRUNC('hour', date_occurred) as hour,
                        COUNT(*) as conflict_count,
                        SUM(fatalities) as total_fatalities
                    FROM conflicts 
                    WHERE date_occurred >= NOW() - INTERVAL '48 hours'
                    GROUP BY DATE_TRUNC('hour', date_occurred)
                ),
                stats AS (
                    SELECT 
                        AVG(conflict_count) as avg_count,
                        STDDEV(conflict_count) as std_count,
                        AVG(total_fatalities) as avg_fatalities,
                        STDDEV(total_fatalities) as std_fatalities
                    FROM hourly_counts
                    WHERE hour >= NOW() - INTERVAL '24 hours'
                )
                SELECT 
                    hc.hour,
                    hc.conflict_count,
                    hc.total_fatalities,
                    s.avg_count,
                    s.std_count,
                    ABS(hc.conflict_count - s.avg_count) / NULLIF(s.std_count, 0) as z_score_count,
                    ABS(hc.total_fatalities - s.avg_fatalities) / NULLIF(s.std_fatalities, 0) as z_score_fatalities
                FROM hourly_counts hc, stats s
                WHERE hc.hour >= NOW() - INTERVAL '6 hours'
                AND (
                    ABS(hc.conflict_count - s.avg_count) > (2 * s.std_count)
                    OR ABS(hc.total_fatalities - s.avg_fatalities) > (2 * s.std_fatalities)
                )
            """)
            
            spike_results = db.execute(spike_query).fetchall()
            
            for row in spike_results:
                anomalies.append({
                    'type': 'spike',
                    'severity': 'high' if row.z_score_count > 3 or row.z_score_fatalities > 3 else 'medium',
                    'timestamp': row.hour,
                    'description': f"Unusual spike detected: {row.conflict_count} conflicts, {row.total_fatalities} fatalities",
                    'metrics': {
                        'conflicts': row.conflict_count,
                        'fatalities': row.total_fatalities,
                        'z_score_count': row.z_score_count,
                        'z_score_fatalities': row.z_score_fatalities
                    }
                })
            
            # Check for geographic clustering
            cluster_query = text("""
                WITH location_clusters AS (
                    SELECT 
                        l.state,
                        COUNT(*) as conflict_count,
                        SUM(c.fatalities) as total_fatalities,
                        DATE_TRUNC('day', c.date_occurred) as day
                    FROM conflicts c
                    JOIN locations l ON c.location_id = l.id
                    WHERE c.date_occurred >= NOW() - INTERVAL '24 hours'
                    GROUP BY l.state, DATE_TRUNC('day', c.date_occurred)
                ),
                state_averages AS (
                    SELECT 
                        state,
                        AVG(conflict_count) as avg_conflicts,
                        STDDEV(conflict_count) as std_conflicts
                    FROM location_clusters
                    WHERE day >= NOW() - INTERVAL '7 days'
                    GROUP BY state
                )
                SELECT 
                    lc.state,
                    lc.conflict_count,
                    lc.total_fatalities,
                    lc.day,
                    sa.avg_conflicts,
                    sa.std_conflicts,
                    (lc.conflict_count - sa.avg_conflicts) / NULLIF(sa.std_conflicts, 0) as z_score
                FROM location_clusters lc
                JOIN state_averages sa ON lc.state = sa.state
                WHERE lc.day >= NOW() - INTERVAL '1 days'
                AND lc.conflict_count > (sa.avg_conflicts + 2 * sa.std_conflicts)
            """)
            
            cluster_results = db.execute(cluster_query).fetchall()
            
            for row in cluster_results:
                anomalies.append({
                    'type': 'geographic_cluster',
                    'severity': 'high' if row.z_score > 3 else 'medium',
                    'location': row.state,
                    'timestamp': row.day,
                    'description': f"Unusual clustering in {row.state}: {row.conflict_count} conflicts",
                    'metrics': {
                        'conflicts': row.conflict_count,
                        'fatalities': row.total_fatalities,
                        'z_score': row.z_score
                    }
                })
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {str(e)}")
            return []

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
                DATE(date_occurred) as report_date,
                COUNT(*) as total_conflicts,
                SUM(fatalities) as total_fatalities,
                COUNT(DISTINCT state) as affected_states,
                COUNT(DISTINCT event_type) as event_types,
                COUNT(DISTINCT source) as sources
            FROM conflicts c
            JOIN locations l ON c.location_id = l.id
            WHERE date_occurred >= CURRENT_DATE - INTERVAL '1 day'
            GROUP BY DATE(date_occurred)
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
                l.state,
                COUNT(*) as conflict_count,
                SUM(c.fatalities) as fatalities
            FROM conflicts c
            JOIN locations l ON c.location_id = l.id
            WHERE date_occurred >= CURRENT_DATE - INTERVAL '1 day'
            GROUP BY l.state
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
            FROM conflicts
            WHERE date_occurred >= CURRENT_DATE - INTERVAL '1 day'
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
        
        # Send report (would implement email/Slack delivery)
        # send_daily_report(report)
        
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
                MAX(date_occurred) as latest_event,
                COUNT(*) as events_today
            FROM conflicts
            WHERE created_at >= CURRENT_DATE
        """)
        
        result = db.execute(query).fetchone()
        
        if not result:
            return {
                'status': 'no_data',
                'message': 'No data found'
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
            'data_age_hours': data_age_hours,
            'is_stale': is_stale,
            'status': 'stale' if is_stale else 'fresh'
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
