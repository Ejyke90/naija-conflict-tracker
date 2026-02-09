"""
System Automation API Endpoints

Provides API endpoints for:
- Scheduler status and control
- Automation execution logs
- System heartbeat monitoring
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from app.db.database import get_db
from app.services.scheduler_service import get_scheduler
from app.api.deps import get_current_active_user
from pydantic import BaseModel
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


class TriggerJobRequest(BaseModel):
    job_id: str


class SchedulerControlRequest(BaseModel):
    action: str  # 'pause' or 'resume'


@router.get("/scheduler/status")
async def get_scheduler_status():
    """
    Get current scheduler status
    
    Returns information about:
    - Scheduler running state
    - Active jobs with next run times
    - Last execution details
    """
    try:
        scheduler = get_scheduler()
        if scheduler is None:
            return {
                "status": "unavailable",
                "message": "Scheduler is not configured",
                "running": False,
                "jobs": []
            }
        return scheduler.get_status()
    except Exception as e:
        logger.error(f"Error getting scheduler status: {e}", exc_info=True)
        return {
            "status": "error",
            "message": f"Failed to get scheduler status: {str(e)}",
            "running": False,
            "jobs": []
        }


@router.post("/scheduler/trigger")
async def trigger_job(
    request: TriggerJobRequest,
    current_user = Depends(get_current_active_user)
):
    """
    Manually trigger a scheduled job immediately
    
    Requires authentication with 'analyst' or 'admin' role
    """
    # Check permissions (only analysts and admins can trigger)
    if current_user.role not in ['analyst', 'admin']:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    scheduler = get_scheduler()
    
    try:
        scheduler.trigger_job(request.job_id)
        return {
            "message": f"Job {request.job_id} triggered successfully",
            "job_id": request.job_id
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/scheduler/control")
async def control_scheduler(
    request: SchedulerControlRequest,
    current_user = Depends(get_current_active_user)
):
    """
    Pause or resume scheduler
    
    Requires authentication with 'admin' role
    """
    # Check permissions (only admins can control scheduler)
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Admin role required")
    
    scheduler = get_scheduler()
    
    try:
        if request.action == 'pause':
            scheduler.pause()
            return {"message": "Scheduler paused successfully"}
        elif request.action == 'resume':
            scheduler.resume()
            return {"message": "Scheduler resumed successfully"}
        else:
            raise HTTPException(status_code=400, detail="Invalid action. Use 'pause' or 'resume'")
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/automation/logs")
async def get_automation_logs(
    limit: int = 100,
    status: Optional[str] = None
):
    """
    Get automation execution logs
    
    Query parameters:
    - limit: Maximum number of logs to return (default: 100)
    - status: Filter by status ('success' or 'failure')
    """
    scheduler = get_scheduler()
    logs = scheduler.get_logs(limit=limit, status_filter=status)
    
    return {
        "logs": logs,
        "count": len(logs),
        "filters": {
            "limit": limit,
            "status": status
        }
    }


@router.get("/system/heartbeat")
async def get_system_heartbeat(db: Session = Depends(get_db)):
    """
    Get comprehensive system heartbeat
    
    Returns:
    - Scheduler status
    - Database connection health
    - Recent activity metrics
    """
    scheduler = get_scheduler()
    scheduler_status = scheduler.get_status()
    
    # Check database health
    try:
        db.execute("SELECT 1")
        db_healthy = True
    except:
        db_healthy = False
    
    # Get recent activity stats
    from sqlalchemy import text
    try:
        result = db.execute(text("""
            SELECT 
                COUNT(*) as total_events,
                COUNT(CASE WHEN created_at >= NOW() - INTERVAL '24 hours' THEN 1 END) as events_last_24h,
                COUNT(CASE WHEN created_at >= NOW() - INTERVAL '1 hour' THEN 1 END) as events_last_hour
            FROM conflict_events_new
        """)).first()
        
        activity_stats = {
            "total_events": result[0] if result else 0,
            "events_last_24h": result[1] if result else 0,
            "events_last_hour": result[2] if result else 0
        }
    except:
        activity_stats = {}
    
    return {
        "status": "healthy" if (scheduler_status['status'] == 'running' and db_healthy) else "degraded",
        "scheduler": scheduler_status,
        "database": {
            "connected": db_healthy
        },
        "activity": activity_stats,
        "timestamp": __import__('datetime').datetime.utcnow().isoformat()
    }


@router.get("/system/metrics")
async def get_system_metrics(db: Session = Depends(get_db)):
    """
    Get system performance metrics
    
    Returns statistics about:
    - Automation execution performance
    - Data processing throughput
    - Error rates
    """
    scheduler = get_scheduler()
    logs = scheduler.get_logs(limit=100)
    
    # Calculate success rate
    if logs:
        successful = sum(1 for log in logs if log['status'] == 'success')
        total = len(logs)
        success_rate = (successful / total) * 100 if total > 0 else 0
        
        # Calculate average duration
        durations = [log['duration_seconds'] for log in logs if log['status'] == 'success']
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        # Recent errors
        recent_errors = [log for log in logs if log['status'] == 'failure'][:5]
    else:
        success_rate = 0
        avg_duration = 0
        recent_errors = []
    
    return {
        "automation": {
            "total_executions": len(logs),
            "success_rate": round(success_rate, 2),
            "average_duration_seconds": round(avg_duration, 2),
            "recent_failures": recent_errors
        },
        "timestamp": __import__('datetime').datetime.utcnow().isoformat()
    }
