"""
Alert API Endpoints

Provides API endpoints for high-risk conflict event alerts.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from app.db.database import get_db
from app.services.alert_service import get_alert_service
from app.core.auth import get_current_active_user
from pydantic import BaseModel

router = APIRouter()


class AcknowledgeAlertRequest(BaseModel):
    notes: Optional[str] = None


class ResolveAlertRequest(BaseModel):
    resolution_notes: Optional[str] = None
    resolution_actions: Optional[Dict[str, Any]] = None


@router.get("/active")
async def get_active_alerts(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get active (unresolved) high-risk alerts
    
    Query parameters:
    - limit: Maximum number of alerts to return (1-100, default: 20)
    """
    alert_service = get_alert_service()
    alerts = await alert_service.get_active_alerts(db, limit=limit)
    
    return {
        "alerts": alerts,
        "count": len(alerts),
        "threshold": alert_service.risk_threshold
    }


@router.get("/recent")
async def get_recent_alerts(
    hours: int = Query(24, ge=1, le=168),  # 1 hour to 1 week
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get recent alerts within specified time window
    
    Query parameters:
    - hours: Time window in hours (1-168, default: 24)
    - limit: Maximum number of alerts to return (1-100, default: 50)
    """
    alert_service = get_alert_service()
    alerts = await alert_service.get_recent_alerts(db, hours=hours, limit=limit)
    
    return {
        "alerts": alerts,
        "count": len(alerts),
        "time_window_hours": hours
    }


@router.get("/poll")
async def poll_for_alerts(
    since: Optional[str] = Query(None, description="ISO 8601 timestamp"),
    db: Session = Depends(get_db)
):
    """
    Poll for new alerts since last check (optimized for frontend polling)
    
    Query parameters:
    - since: ISO timestamp of last poll (e.g., "2026-02-08T15:30:00Z")
    
    If 'since' is not provided, returns alerts from the last 5 minutes.
    """
    from datetime import datetime, timedelta
    from app.models.alert import AlertEvent
    from sqlalchemy import desc
    
    # Parse since timestamp
    if since:
        try:
            since_dt = datetime.fromisoformat(since.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid timestamp format")
    else:
        # Default to last 5 minutes if no timestamp provided
        since_dt = datetime.utcnow() - timedelta(minutes=5)
    
    # Get new alerts
    alerts = db.query(AlertEvent).filter(
        AlertEvent.created_at > since_dt
    ).order_by(
        desc(AlertEvent.created_at)
    ).limit(20).all()
    
    alert_service = get_alert_service()
    
    return {
        "alerts": [alert_service._alert_to_dict(alert) for alert in alerts],
        "count": len(alerts),
        "since": since_dt.isoformat(),
        "server_time": datetime.utcnow().isoformat()
    }


@router.post("/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: int,
    request: AcknowledgeAlertRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Acknowledge an alert
    
    Marks alert as acknowledged by the current user.
    """
    alert_service = get_alert_service()
    
    success = await alert_service.acknowledge_alert(
        alert_id=alert_id,
        user_id=current_user.id,
        notes=request.notes,
        db=db
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return {
        "message": "Alert acknowledged successfully",
        "alert_id": alert_id,
        "acknowledged_by": current_user.email
    }


@router.post("/{alert_id}/resolve")
async def resolve_alert(
    alert_id: int,
    request: ResolveAlertRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Resolve an alert
    
    Marks alert as resolved by the current user.
    Requires 'analyst' or 'admin' role.
    """
    if current_user.role not in ['analyst', 'admin']:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    alert_service = get_alert_service()
    
    success = await alert_service.resolve_alert(
        alert_id=alert_id,
        user_id=current_user.id,
        resolution_notes=request.resolution_notes,
        resolution_actions=request.resolution_actions,
        db=db
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return {
        "message": "Alert resolved successfully",
        "alert_id": alert_id,
        "resolved_by": current_user.email
    }


@router.get("/statistics")
async def get_alert_statistics(
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db)
):
    """
    Get alert statistics and metrics
    
    Query parameters:
    - days: Number of days to analyze (1-90, default: 7)
    """
    from datetime import datetime, timedelta
    from app.models.alert import AlertEvent
    from sqlalchemy import func, and_
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Total alerts
    total_alerts = db.query(func.count(AlertEvent.id)).filter(
        AlertEvent.created_at >= cutoff_date
    ).scalar()
    
    # Alerts by type
    alerts_by_type = db.query(
        AlertEvent.alert_type,
        func.count(AlertEvent.id).label('count')
    ).filter(
        AlertEvent.created_at >= cutoff_date
    ).group_by(AlertEvent.alert_type).all()
    
    # Alerts by status
    alerts_by_status = db.query(
        AlertEvent.status,
        func.count(AlertEvent.id).label('count')
    ).filter(
        AlertEvent.created_at >= cutoff_date
    ).group_by(AlertEvent.status).all()
    
    # Average response time (time to acknowledgment)
    avg_ack_time = db.query(
        func.avg(
            func.extract('epoch', AlertEvent.acknowledged_at - AlertEvent.created_at)
        )
    ).filter(
        and_(
            AlertEvent.created_at >= cutoff_date,
            AlertEvent.acknowledged_at.isnot(None)
        )
    ).scalar()
    
    # Average resolution time
    avg_resolve_time = db.query(
        func.avg(
            func.extract('epoch', AlertEvent.resolved_at - AlertEvent.created_at)
        )
    ).filter(
        and_(
            AlertEvent.created_at >= cutoff_date,
            AlertEvent.resolved_at.isnot(None)
        )
    ).scalar()
    
    return {
        "period_days": days,
        "total_alerts": total_alerts or 0,
        "by_type": {row[0]: row[1] for row in alerts_by_type},
        "by_status": {row[0]: row[1] for row in alerts_by_status},
        "metrics": {
            "avg_acknowledgment_time_seconds": round(avg_ack_time or 0, 2),
            "avg_resolution_time_seconds": round(avg_resolve_time or 0, 2)
        }
    }
