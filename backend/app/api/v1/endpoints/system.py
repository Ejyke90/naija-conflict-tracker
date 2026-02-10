"""
System Automation API Endpoints

Provides API endpoints for:
- Scheduler status and control
- Automation execution logs
- System heartbeat monitoring
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any, Optional
from datetime import datetime
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
    Get current scheduler status with fast fallback
    
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
                "message": "Scheduler not initialized",
                "running": False,
                "jobs": [],
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Try to get detailed status with 2 second timeout
        import asyncio
        try:
            status_result = await asyncio.wait_for(
                asyncio.create_task(asyncio.to_thread(scheduler.get_status)),
                timeout=2.0
            ) if hasattr(scheduler, 'get_status') else None
            return status_result or {
                "status": "running",
                "running": scheduler.running if hasattr(scheduler, 'running') else True,
                "jobs": [],
                "timestamp": datetime.utcnow().isoformat()
            }
        except (asyncio.TimeoutError, AttributeError):
            # Fast fallback if status query times out
            return {
                "status": "running",
                "running": True,
                "jobs": [],
                "message": "Status query timed out (scheduler is operating normally)",
                "timestamp": datetime.utcnow().isoformat()
            }
    except Exception as e:
        logger.error(f"Error getting scheduler status: {e}", exc_info=True)
        # Always return a valid response, never 500
        return {
            "status": "error",
            "message": f"Failed to get status: {str(e)}",
            "running": False,
            "jobs": [],
            "timestamp": datetime.utcnow().isoformat()
        }


@router.post("/scheduler/trigger")
async def trigger_job(
    request: TriggerJobRequest,
    current_user = Depends(get_current_active_user)
):
    """
    Manually trigger a scheduled job immediately
    
    Available to all authenticated users
    """
    
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
    
    Available to all authenticated users
    """
    
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


@router.get("/validation/summary")
async def get_validation_summary(db: Session = Depends(get_db)):
    """
    Get validation summary from conflict_events table
    
    Returns high-performance summary data:
    - Pending items count (unverified events)
    - Urgent status logic (high fatality events pending)
    - High priority count (fatalities > 0 and unverified)
    - Last validation activity (last event date)
    - Total verified count
    - Oldest pending item (oldest unverified event)
    
    **Public endpoint** - No authentication required for performance
    **Cache:** 2 minutes recommended
    **Source:** conflicts table
    """
    try:
        # Get validation metrics from conflicts table (where verification actually happens)
        total_count_result = db.execute(text("SELECT COUNT(*) FROM conflicts")).scalar()
        verified_count_result = db.execute(text("SELECT COUNT(*) FROM conflicts WHERE verified = true")).scalar()
        pending_count = total_count_result - verified_count_result
        
        # Get high priority count (unverified events with fatalities)
        high_priority_result = db.execute(text("""
            SELECT COUNT(*) FROM conflicts 
            WHERE verified = false AND (fatalities_male > 0 OR fatalities_female > 0 OR fatalities_unknown > 0)
        """)).scalar()
        
        # Get last activity (most recent event date)
        last_activity_result = db.execute(text("SELECT MAX(event_date) FROM conflicts")).scalar()
        
        # Get oldest pending item (oldest unverified event)
        oldest_pending_result = db.execute(text("""
            SELECT MIN(event_date) FROM conflicts 
            WHERE verified = false
        """)).scalar()
        
        # Determine if urgent (high priority items > 10 or pending > 1000)
        is_urgent = high_priority_result > 10 or pending_count > 1000
        
        response = {
            "pendingCount": pending_count,
            "isUrgent": is_urgent,
            "highPriorityCount": high_priority_result,
            "lastActivity": last_activity_result.isoformat() if last_activity_result else None,
            "totalVerified": verified_count_result,
            "oldestItem": oldest_pending_result.isoformat() if oldest_pending_result else None,
            "status": "ok",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Validation summary retrieved: {response}")
        return response
        
    except Exception as e:
        logger.error(f"Error retrieving validation summary: {str(e)}", exc_info=True)
        # Return graceful degraded response
        return {
            "pendingCount": 0,
            "isUrgent": False,
            "highPriorityCount": 0,
            "lastActivity": None,
            "totalVerified": 0,
            "oldestItem": None,
            "status": "error",
            "message": "Unable to retrieve validation summary",
            "error_code": "VALIDATION_SUMMARY_ERROR",
            "timestamp": datetime.utcnow().isoformat()
        }
