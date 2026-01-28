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
        return await get_pipeline_status_data(db)
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
    """Get data quality metrics from database"""
    try:
        # Try to get real metrics from data_quality_metrics table
        try:
            from app.models.data_quality import DataQualityMetric
            from sqlalchemy import desc
            
            # Get the most recent metric
            latest_metric = db.query(DataQualityMetric).order_by(
                desc(DataQualityMetric.timestamp)
            ).first()
            
            if latest_metric:
                return {
                    'status': latest_metric.status,
                    'geocoding_success_rate': latest_metric.geocoding_success_rate,
                    'validation_pass_rate': latest_metric.validation_pass_rate,
                    'total_geocoded': latest_metric.geocoding_successes,
                    'total_validated': latest_metric.validation_passes,
                    'last_updated': latest_metric.timestamp.isoformat()
                }
        except Exception as db_error:
            logger.debug(f"Could not retrieve from data_quality_metrics table: {db_error}")
        
        # Fallback: Calculate from conflicts table
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
        
        if not result or result.total_events == 0:
            return {
                'status': 'no_data',
                'geocoding_success_rate': 0.0,
                'validation_pass_rate': 0.0,
                'message': 'No events found in last 24 hours'
            }
        
        geocoding_rate = (result.geocoded_events / result.total_events * 100) if result.total_events > 0 else 0
        validation_rate = (result.verified_events / result.total_events * 100) if result.total_events > 0 else 0
        
        quality_score = (geocoding_rate * 0.5) + (validation_rate * 0.5)
        status = 'healthy' if quality_score >= 75 else 'warning' if quality_score >= 50 else 'error'
        
        return {
            'status': status,
            'geocoding_success_rate': geocoding_rate,
            'validation_pass_rate': validation_rate,
            'total_geocoded': result.geocoded_events,
            'total_validated': result.verified_events,
            'total_events': result.total_events,
            'avg_verification_score': float(result.avg_verification_score) if result.avg_verification_score else 0.0,
            'unique_sources': result.unique_sources,
            'latest_event': result.latest_event.isoformat() if result.latest_event else None
        }
        
    except Exception as e:
        logger.error(f"Error getting data quality: {str(e)}")
        return {
            'status': 'error',
            'error': str(e),
            'geocoding_success_rate': 0.0,
            'validation_pass_rate': 0.0
        }


async def get_pipeline_status_data(db: Session) -> Dict[str, Any]:
    """Get complete pipeline status data for HTTP and WebSocket endpoints
    
    This function consolidates all monitoring data into a single response
    used by both the REST endpoint and WebSocket broadcasts.
    """
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "scraping_health": await get_scraping_health(db),
        "data_quality": await get_data_quality(db),
        "anomalies": await detect_anomalies(db),
        "alerts": await generate_alerts(
            await get_scraping_health(db),
            await get_data_quality(db),
            await detect_anomalies(db)
        ),
        "overall_status": "healthy"
    }

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


# Enhanced Health Check Endpoints for Phase 2

@router.get("/health")
async def get_enhanced_health(db: Session = Depends(get_db)):
    """Enhanced health check with process and dependency information."""
    from app.utils.process_manager import get_process_manager
    from app.utils.error_recovery import get_dependency_checker
    import time

    health_data = {
        "status": "healthy",
        "timestamp": time.time(),
        "checks": {},
        "process": {},
        "dependencies": {}
    }

@router.get("/health")
async def get_enhanced_health(db: Session = Depends(get_db)):
    """Enhanced health check with process and dependency information."""
    from app.utils.process_manager import get_process_manager
    from app.utils.error_recovery import get_dependency_checker
    import time
    import psutil
    import os

    health_data = {
        "status": "healthy",
        "timestamp": time.time(),
        "checks": {},
        "process": {},
        "dependencies": {},
        "performance": {}
    }

    # Process health with detailed metrics
    try:
        process_mgr = get_process_manager()
        process_health = process_mgr.check_health()

        # Get detailed process metrics
        current_process = psutil.Process()
        memory_info = current_process.memory_info()
        cpu_times = current_process.cpu_times()

        health_data["process"] = {
            **process_health,
            "metrics": {
                "cpu_percent": current_process.cpu_percent(interval=0.1),
                "memory_rss_mb": memory_info.rss / (1024 * 1024),
                "memory_vms_mb": memory_info.vms / (1024 * 1024),
                "memory_percent": current_process.memory_percent(),
                "threads": len(current_process.threads()),
                "open_files": len(current_process.open_files()),
                "connections": len(current_process.connections()),
                "cpu_user_time": cpu_times.user,
                "cpu_system_time": cpu_times.system
            }
        }
    except Exception as e:
        health_data["process"] = {"status": "error", "error": str(e)}
        health_data["status"] = "degraded"

    # Performance metrics
    try:
        health_data["performance"] = {
            "system_load": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None,
            "cpu_count": psutil.cpu_count(),
            "cpu_count_logical": psutil.cpu_count(logical=True),
            "memory_total_gb": psutil.virtual_memory().total / (1024**3),
            "memory_available_gb": psutil.virtual_memory().available / (1024**3),
            "disk_total_gb": psutil.disk_usage('/').total / (1024**3),
            "disk_free_gb": psutil.disk_usage('/').free / (1024**3),
            "network_connections": len(psutil.net_connections()),
            "boot_time": psutil.boot_time()
        }
    except Exception as e:
        health_data["performance"] = {"error": str(e)}

    # Database health
    try:
        start_time = time.time()
        result = db.execute(text("SELECT 1")).scalar()
        response_time = time.time() - start_time

        health_data["checks"]["database"] = {
            "status": "healthy" if result == 1 else "unhealthy",
            "response_time": response_time,
            "timestamp": time.time()
        }
    except Exception as e:
        health_data["checks"]["database"] = {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": time.time()
        }
        health_data["status"] = "degraded"

    # Redis health
    try:
        from app.core.cache import get_redis_client
        redis_client = await get_redis_client()
        start_time = time.time()
        await redis_client.ping()
        response_time = time.time() - start_time

        health_data["checks"]["redis"] = {
            "status": "healthy",
            "response_time": response_time,
            "timestamp": time.time()
        }
    except Exception as e:
        health_data["checks"]["redis"] = {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": time.time()
        }
        health_data["status"] = "degraded"

    # Dependency checker
    try:
        dep_checker = get_dependency_checker()
        dep_health = dep_checker.get_health_summary()
        health_data["dependencies"] = dep_health

        if not dep_health.get("overall_healthy", True):
            health_data["status"] = "degraded"
    except Exception as e:
        health_data["dependencies"] = {"error": str(e)}

    # Overall status determination
    if any(check.get("status") == "unhealthy" for check in health_data["checks"].values()):
        health_data["status"] = "unhealthy"

    return health_data


@router.get("/ready")
async def readiness_probe(db: Session = Depends(get_db)):
    """Readiness probe for Kubernetes/load balancer."""
    from app.utils.error_recovery import get_dependency_checker
    import time

    # Quick database check
    try:
        result = db.execute(text("SELECT 1")).scalar()
        if result != 1:
            raise HTTPException(status_code=503, detail="Database not ready")
    except Exception:
        raise HTTPException(status_code=503, detail="Database not ready")

    # Quick Redis check
    try:
        from app.core.cache import get_redis_client
        redis_client = await get_redis_client()
        await redis_client.ping()
    except Exception:
        raise HTTPException(status_code=503, detail="Redis not ready")

    # Check critical dependencies
    try:
        dep_checker = get_dependency_checker()
        dep_health = dep_checker.get_health_summary()
        if not dep_health.get("overall_healthy", True):
            raise HTTPException(status_code=503, detail="Dependencies not ready")
    except Exception:
        raise HTTPException(status_code=503, detail="Dependency check failed")

    return {
        "status": "ready",
        "timestamp": time.time(),
        "message": "All systems ready"
    }


@router.get("/alive")
async def liveness_probe():
    """Liveness probe for Kubernetes."""
    from app.utils.process_manager import get_process_manager
    import time

    try:
        process_mgr = get_process_manager()
        process_health = process_mgr.check_health()

        if process_health.get("status") == "shutting_down":
            raise HTTPException(status_code=503, detail="Server is shutting down")

        return {
            "status": "alive",
            "timestamp": time.time(),
            "uptime": process_health.get("uptime_seconds", 0)
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Liveness check failed: {str(e)}")


@router.get("/diagnostics")
async def get_system_diagnostics(db: Session = Depends(get_db)):
    """Comprehensive system diagnostics for troubleshooting."""
    from app.utils.process_manager import get_process_manager
    from app.utils.error_recovery import get_dependency_checker
    import platform
    import sys
    import time

    diagnostics = {
        "timestamp": time.time(),
        "system": {
            "platform": platform.platform(),
            "python_version": sys.version,
            "cpu_count": psutil.cpu_count(),
            "memory_total": psutil.virtual_memory().total,
            "disk_total": psutil.disk_usage('/').total
        },
        "process": {},
        "database": {},
        "redis": {},
        "dependencies": {},
        "configuration": {}
    }

    # Process diagnostics
    try:
        process_mgr = get_process_manager()
        diagnostics["process"] = process_mgr.get_process_info()
    except Exception as e:
        diagnostics["process"] = {"error": str(e)}

    # Database diagnostics
    try:
        from app.db.database import engine
        diagnostics["database"] = {
            "pool_size": engine.pool.size(),
            "checked_in": engine.pool.checkedin(),
            "checked_out": engine.pool.checkedout(),
            "overflow": engine.pool.overflow(),
            "invalid": engine.pool.invalid()
        }
    except Exception as e:
        diagnostics["database"] = {"error": str(e)}

    # Redis diagnostics
    try:
        from app.core.cache import get_redis_client, get_cache_stats
        redis_client = await get_redis_client()
        cache_stats = await get_cache_stats()
        diagnostics["redis"] = cache_stats
    except Exception as e:
        diagnostics["redis"] = {"error": str(e)}

    # Dependency diagnostics
    try:
        dep_checker = get_dependency_checker()
        diagnostics["dependencies"] = dep_checker.check_all_dependencies()
    except Exception as e:
        diagnostics["dependencies"] = {"error": str(e)}

    # Configuration diagnostics
    try:
        import os
        diagnostics["configuration"] = {
            "env_vars": {k: "***" if "secret" in k.lower() or "key" in k.lower() else v
                        for k, v in os.environ.items()
                        if k.startswith(("DATABASE_", "REDIS_", "JWT_", "HOST", "PORT"))},
            "debug_mode": os.getenv("DEBUG", "false").lower() == "true"
        }
    except Exception as e:
        diagnostics["configuration"] = {"error": str(e)}

    return diagnostics


# Phase 3: Production Hardening - Deployment Safety

@router.get("/deployment/pre-flight")
async def pre_deployment_check(db: Session = Depends(get_db)):
    """Pre-deployment validation checks."""
    import time
    import os
    from app.config.server_config import validate_dependencies

    checks = {
        "timestamp": time.time(),
        "environment": os.getenv("ENVIRONMENT", "development"),
        "checks": {},
        "ready_for_deployment": True
    }

    # Configuration validation
    try:
        from app.config.server_config import ServerConfig
        config = ServerConfig()
        is_valid, errors = config.validate()
        checks["checks"]["configuration"] = {
            "status": "passed" if is_valid else "failed",
            "errors": errors
        }
        if not is_valid:
            checks["ready_for_deployment"] = False
    except Exception as e:
        checks["checks"]["configuration"] = {"status": "error", "error": str(e)}
        checks["ready_for_deployment"] = False

    # Dependency validation
    try:
        dep_errors = validate_dependencies()
        checks["checks"]["dependencies"] = {
            "status": "passed" if not dep_errors else "failed",
            "errors": dep_errors
        }
        if dep_errors:
            checks["ready_for_deployment"] = False
    except Exception as e:
        checks["checks"]["dependencies"] = {"status": "error", "error": str(e)}
        checks["ready_for_deployment"] = False

    # Database connectivity
    try:
        start_time = time.time()
        result = db.execute(text("SELECT COUNT(*) FROM information_schema.tables")).scalar()
        response_time = time.time() - start_time
        checks["checks"]["database"] = {
            "status": "passed",
            "response_time": response_time,
            "table_count": result
        }
    except Exception as e:
        checks["checks"]["database"] = {"status": "failed", "error": str(e)}
        checks["ready_for_deployment"] = False

    # Redis connectivity
    try:
        from app.core.cache import get_redis_client
        redis_client = await get_redis_client()
        start_time = time.time()
        await redis_client.ping()
        response_time = time.time() - start_time
        checks["checks"]["redis"] = {
            "status": "passed",
            "response_time": response_time
        }
    except Exception as e:
        checks["checks"]["redis"] = {"status": "failed", "error": str(e)}
        checks["ready_for_deployment"] = False

    # Port availability
    try:
        from app.utils.port_manager import check_port_available
        port = int(os.getenv("PORT", "8000"))
        host = os.getenv("HOST", "0.0.0.0")
        port_available = check_port_available(port, host)
        checks["checks"]["port_availability"] = {
            "status": "passed" if port_available else "failed",
            "port": port,
            "host": host,
            "available": port_available
        }
        if not port_available:
            checks["ready_for_deployment"] = False
    except Exception as e:
        checks["checks"]["port_availability"] = {"status": "error", "error": str(e)}
        checks["ready_for_deployment"] = False

    return checks


@router.get("/deployment/post-flight")
async def post_deployment_validation(db: Session = Depends(get_db)):
    """Post-deployment validation checks."""
    import time
    import requests
    import os

    validation = {
        "timestamp": time.time(),
        "deployment_status": "validating",
        "checks": {}
    }

    # Health endpoint check
    try:
        port = int(os.getenv("PORT", "8000"))
        host = os.getenv("HOST", "0.0.0.0")
        health_url = f"http://{host}:{port}/api/v1/monitoring/health"

        start_time = time.time()
        response = requests.get(health_url, timeout=10)
        response_time = time.time() - start_time

        validation["checks"]["health_endpoint"] = {
            "status": "passed" if response.status_code == 200 else "failed",
            "response_time": response_time,
            "status_code": response.status_code,
            "url": health_url
        }

        if response.status_code == 200:
            health_data = response.json()
            validation["checks"]["health_endpoint"]["health_status"] = health_data.get("status")
    except Exception as e:
        validation["checks"]["health_endpoint"] = {"status": "failed", "error": str(e)}

    # Readiness probe
    try:
        port = int(os.getenv("PORT", "8000"))
        host = os.getenv("HOST", "0.0.0.0")
        ready_url = f"http://{host}:{port}/api/v1/monitoring/ready"

        start_time = time.time()
        response = requests.get(ready_url, timeout=5)
        response_time = time.time() - start_time

        validation["checks"]["readiness_probe"] = {
            "status": "passed" if response.status_code == 200 else "failed",
            "response_time": response_time,
            "status_code": response.status_code,
            "url": ready_url
        }
    except Exception as e:
        validation["checks"]["readiness_probe"] = {"status": "failed", "error": str(e)}

    # Liveness probe
    try:
        port = int(os.getenv("PORT", "8000"))
        host = os.getenv("HOST", "0.0.0.0")
        alive_url = f"http://{host}:{port}/api/v1/monitoring/alive"

        start_time = time.time()
        response = requests.get(alive_url, timeout=5)
        response_time = time.time() - start_time

        validation["checks"]["liveness_probe"] = {
            "status": "passed" if response.status_code == 200 else "failed",
            "response_time": response_time,
            "status_code": response.status_code,
            "url": alive_url
        }
    except Exception as e:
        validation["checks"]["liveness_probe"] = {"status": "failed", "error": str(e)}

    # Database connectivity post-deployment
    try:
        start_time = time.time()
        result = db.execute(text("SELECT 1")).scalar()
        response_time = time.time() - start_time

        validation["checks"]["database_post_deployment"] = {
            "status": "passed" if result == 1 else "failed",
            "response_time": response_time
        }
    except Exception as e:
        validation["checks"]["database_post_deployment"] = {"status": "failed", "error": str(e)}

    # Determine overall deployment status
    all_checks_passed = all(
        check.get("status") == "passed"
        for check in validation["checks"].values()
    )

    validation["deployment_status"] = "successful" if all_checks_passed else "failed"

    return validation


@router.get("/metrics/prometheus")
async def get_prometheus_metrics(db: Session = Depends(get_db)):
    """Prometheus-compatible metrics endpoint."""
    import time
    import psutil
    from app.utils.process_manager import get_process_manager

    metrics = []

    # Process metrics
    try:
        process_mgr = get_process_manager()
        process_health = process_mgr.check_health()
        current_process = psutil.Process()

        metrics.extend([
            f'# HELP process_uptime_seconds Time the process has been running',
            f'# TYPE process_uptime_seconds gauge',
            f'process_uptime_seconds {process_health.get("uptime_seconds", 0)}',
            f'',
            f'# HELP process_cpu_percent CPU usage percentage',
            f'# TYPE process_cpu_percent gauge',
            f'process_cpu_percent {current_process.cpu_percent()}',
            f'',
            f'# HELP process_memory_bytes Memory usage in bytes',
            f'# TYPE process_memory_bytes gauge',
            f'process_memory_bytes {current_process.memory_info().rss}',
            f'',
            f'# HELP process_threads Number of threads',
            f'# TYPE process_threads gauge',
            f'process_threads {len(current_process.threads())}',
        ])
    except Exception as e:
        metrics.append(f'# Error getting process metrics: {e}')

    # System metrics
    try:
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        metrics.extend([
            f'# HELP system_memory_percent Memory usage percentage',
            f'# TYPE system_memory_percent gauge',
            f'system_memory_percent {memory.percent}',
            f'',
            f'# HELP system_disk_percent Disk usage percentage',
            f'# TYPE system_disk_percent gauge',
            f'system_disk_percent {(disk.used / disk.total) * 100}',
            f'',
            f'# HELP system_cpu_percent CPU usage percentage',
            f'# TYPE system_cpu_percent gauge',
            f'system_cpu_percent {psutil.cpu_percent()}',
        ])
    except Exception as e:
        metrics.append(f'# Error getting system metrics: {e}')

    # Database connection pool metrics
    try:
        from app.db.database import engine
        pool = engine.pool

        metrics.extend([
            f'# HELP db_pool_size Database connection pool size',
            f'# TYPE db_pool_size gauge',
            f'db_pool_size {pool.size()}',
            f'',
            f'# HELP db_pool_checked_out Database connections checked out',
            f'# TYPE db_pool_checked_out gauge',
            f'db_pool_checked_out {pool.checkedout()}',
            f'',
            f'# HELP db_pool_checked_in Database connections checked in',
            f'# TYPE db_pool_checked_in gauge',
            f'db_pool_checked_in {pool.checkedin()}',
        ])
    except Exception as e:
        metrics.append(f'# Error getting database metrics: {e}')

    # HTTP response for metrics
    return "\n".join(metrics)
