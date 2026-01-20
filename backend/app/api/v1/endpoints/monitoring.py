from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from app.db.database import get_db
from app.core.celery_app import celery_app
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import psutil
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/pipeline-status")
async def get_pipeline_status(db: Session = Depends(get_db)):
    """Get comprehensive pipeline status"""
    try:
        # Get scraping health data
        scraping_health = await get_scraping_health(db)
        
        # Get data quality metrics
        data_quality = await get_data_quality(db)
        
        # Detect anomalies
        anomalies = await detect_anomalies(db)
        
        # Generate alerts
        alerts = await generate_alerts(scraping_health, data_quality, anomalies)
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "scraping_health": scraping_health,
            "data_quality": data_quality,
            "anomalies": anomalies,
            "alerts": alerts,
            "overall_status": "healthy" if not alerts else "alert"
        }
        
    except Exception as e:
        logger.error(f"Error getting pipeline status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/system-metrics")
async def get_system_metrics():
    """Get system resource metrics"""
    try:
        # Get system metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Check Redis connection
        redis_status = 'healthy'
        try:
            inspect = celery_app.control.inspect()
            stats = inspect.stats()
            if not stats:
                redis_status = 'no_workers'
        except Exception as e:
            redis_status = 'error'
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_available_gb": memory.available / (1024**3),
            "disk_percent": (disk.used / disk.total) * 100,
            "disk_free_gb": disk.free / (1024**3),
            "redis_status": redis_status,
            "worker_count": len(stats) if stats else 0,
            "status": "healthy",
            "warnings": []
        }
        
    except Exception as e:
        logger.error(f"Error getting system metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/scraping-status")
async def get_scraping_status_endpoint(db: Session = Depends(get_db)):
    """Get detailed scraping status"""
    try:
        return await get_scraping_health(db)
    except Exception as e:
        logger.error(f"Error getting scraping status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/data-quality")
async def get_data_quality_endpoint(db: Session = Depends(get_db)):
    """Get data quality metrics"""
    try:
        return await get_data_quality(db)
    except Exception as e:
        logger.error(f"Error getting data quality: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/trigger-manual")
async def trigger_manual_scrape(
    background_tasks: BackgroundTasks,
    sources: Optional[List[str]] = None,
    db: Session = Depends(get_db)
):
    """Trigger manual scraping of news sources"""
    try:
        if not sources or sources == ['all']:
            # Trigger full scraping
            task = celery_app.send_task(
                'app.tasks.scraping_tasks.scrape_all_news_sources',
                queue='scraping'
            )
        else:
            # Trigger specific sources
            for source in sources:
                task = celery_app.send_task(
                    'app.tasks.scraping_tasks.scrape_news_source',
                    args=[source],
                    queue='scraping'
                )
        
        return {
            "message": "Scraping task triggered successfully",
            "task_id": task.id,
            "sources": sources or ["all"]
        }
        
    except Exception as e:
        logger.error(f"Error triggering manual scrape: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/task-status/{task_id}")
async def get_task_status(task_id: str):
    """Get status of a specific Celery task"""
    try:
        result = celery_app.AsyncResult(task_id)
        
        return {
            "task_id": task_id,
            "status": result.status,
            "result": result.result if result.ready() else None,
            "date_done": str(result.date_done) if result.date_done else None
        }
        
    except Exception as e:
        logger.error(f"Error getting task status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/worker-status")
async def get_worker_status():
    """Get status of Celery workers"""
    try:
        inspect = celery_app.control.inspect()
        
        # Get active tasks
        active_tasks = inspect.active()
        
        # Get scheduled tasks
        scheduled_tasks = inspect.scheduled()
        
        # Get worker stats
        stats = inspect.stats()
        
        return {
            "workers": list(stats.keys()) if stats else [],
            "active_tasks": active_tasks or {},
            "scheduled_tasks": scheduled_tasks or {},
            "worker_stats": stats or {},
            "total_workers": len(stats) if stats else 0
        }
        
    except Exception as e:
        logger.error(f"Error getting worker status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recent-events")
async def get_recent_events(
    hours: int = 24,
    db: Session = Depends(get_db)
):
    """Get recent conflict events"""
    try:
        query = text("""
            SELECT 
                c.id,
                c.event_type,
                c.fatalities,
                c.date_occurred,
                c.description,
                c.source,
                c.verification_score,
                l.name as location_name,
                l.state as location_state,
                c.created_at
            FROM conflicts c
            JOIN locations l ON c.location_id = l.id
            WHERE c.date_occurred >= NOW() - INTERVAL :hours hours
            ORDER BY c.date_occurred DESC
            LIMIT 100
        """)
        
        results = db.execute(query, {"hours": hours}).fetchall()
        
        events = []
        for row in results:
            events.append({
                "id": row.id,
                "event_type": row.event_type,
                "fatalities": row.fatalities,
                "date_occurred": row.date_occurred.isoformat(),
                "description": row.description,
                "source": row.source,
                "verification_score": row.verification_score,
                "location": {
                    "name": row.location_name,
                    "state": row.location_state
                },
                "created_at": row.created_at.isoformat()
            })
        
        return {
            "events": events,
            "total_events": len(events),
            "timeframe_hours": hours,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting recent events: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Helper functions
async def get_scraping_health(db: Session) -> Dict[str, Any]:
    """Get scraping health metrics"""
    try:
        # For now, return mock data since we don't have task_results table
        # In production, this would query actual task results
        return {
            "overall_status": "healthy",
            "sources": [
                {
                    "source": "punch",
                    "status": "healthy",
                    "success_rate": 0.95,
                    "last_run": (datetime.utcnow() - timedelta(hours=2)).isoformat()
                },
                {
                    "source": "vanguard",
                    "status": "healthy",
                    "success_rate": 0.92,
                    "last_run": (datetime.utcnow() - timedelta(hours=2)).isoformat()
                },
                {
                    "source": "daily_trust",
                    "status": "unhealthy",
                    "success_rate": 0.65,
                    "last_run": (datetime.utcnow() - timedelta(hours=4)).isoformat()
                }
            ],
            "total_sources": 15,
            "failed_sources": 1,
            "avg_success_rate": 0.84
        }
    except Exception as e:
        logger.error(f"Error getting scraping health: {str(e)}")
        return {"status": "error", "error": str(e)}

async def get_data_quality(db: Session) -> Dict[str, Any]:
    """Get data quality metrics"""
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
            'latest_event': result.latest_event.isoformat() if result.latest_event else None
        }
        
    except Exception as e:
        logger.error(f"Error getting data quality: {str(e)}")
        return {'status': 'error', 'error': str(e)}

async def detect_anomalies(db: Session) -> List[Dict[str, Any]]:
    """Detect anomalies in conflict data"""
    try:
        # For now, return mock anomalies
        # In production, this would implement actual anomaly detection
        return [
            {
                "type": "spike",
                "severity": "medium",
                "description": "Unusual spike detected: 15 conflicts in Lagos",
                "timestamp": (datetime.utcnow() - timedelta(hours=3)).isoformat()
            }
        ]
    except Exception as e:
        logger.error(f"Error detecting anomalies: {str(e)}")
        return []

async def generate_alerts(
    scraping_health: Dict[str, Any], 
    quality_data: Dict[str, Any], 
    anomalies: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Generate alerts based on monitoring data"""
    alerts = []
    
    # Health alerts
    if scraping_health.get('overall_status') == 'unhealthy':
        alerts.append({
            'type': 'health',
            'severity': 'high',
            'title': 'Pipeline Health Issues',
            'message': f"{scraping_health['failed_sources']} sources are failing",
            'timestamp': datetime.utcnow().isoformat()
        })
    
    # Quality alerts
    if quality_data.get('quality_score', 100) < 60:
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
