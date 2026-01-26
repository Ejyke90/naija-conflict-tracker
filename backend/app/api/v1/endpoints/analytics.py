from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, timedelta

from app.db.database import get_db
from app.models.conflict import ConflictEvent
from app.models.auth import User
from app.api.deps import require_role

router = APIRouter()


@router.get("/hotspots")
async def get_conflict_hotspots(
    radius_km: int = Query(50, ge=1, le=500),
    min_incidents: int = Query(5, ge=1),
    current_user: User = Depends(require_role("analyst")),
    db: Session = Depends(get_db)
):
    """Get conflict hotspots - areas with high concentration of incidents.
    
    **Requires:** Analyst or Admin role
    """
    
    # Query for high-conflict LGAs in last 6 months
    six_months_ago = datetime.now().date() - timedelta(days=180)
    
    hotspots = db.query(
        ConflictEvent.state,
        ConflictEvent.lga,
        func.count(ConflictEvent.id).label('incident_count'),
        func.sum(ConflictEvent.fatalities).label('total_fatalities'),
        func.sum(ConflictEvent.displaced_persons).label('total_displaced')
    ).filter(
        ConflictEvent.event_date >= six_months_ago
    ).group_by(
        ConflictEvent.state, ConflictEvent.lga
    ).having(
        func.count(ConflictEvent.id) >= min_incidents
    ).order_by(
        func.count(ConflictEvent.id).desc()
    ).all()
    
    return [
        {
            "state": hotspot.state,
            "lga": hotspot.lga,
            "incident_count": hotspot.incident_count,
            "total_fatalities": hotspot.total_fatalities or 0,
            "total_displaced": hotspot.total_displaced or 0,
            "avg_confidence": float(hotspot.avg_confidence or 0),
            "risk_level": calculate_risk_level(hotspot.incident_count, hotspot.total_fatalities or 0)
        }
        for hotspot in hotspots
    ]


@router.get("/trends")
async def get_conflict_trends(
    period: str = Query("monthly", pattern="^(daily|weekly|monthly)$"),
    months: int = Query(12, ge=1, le=60),
    current_user: User = Depends(require_role("analyst")),
    db: Session = Depends(get_db)
):
    """Get conflict trends over time.
    
    **Requires:** Analyst or Admin role
    """
    
    start_date = datetime.now().date() - timedelta(days=months * 30)
    
    if period == "daily":
        date_trunc = func.date_trunc('day', ConflictEvent.event_date)
    elif period == "weekly":
        date_trunc = func.date_trunc('week', ConflictEvent.event_date)
    else:  # monthly
        date_trunc = func.date_trunc('month', ConflictEvent.event_date)
    
    trends = db.query(
        date_trunc.label('period'),
        ConflictEvent.state,
        ConflictEvent.conflict_type,
        func.count(ConflictEvent.id).label('incidents'),
        func.sum(ConflictEvent.fatalities).label('fatalities')
    ).filter(
        ConflictEvent.event_date >= start_date
    ).group_by(
        'period', ConflictEvent.state, ConflictEvent.conflict_type
    ).order_by('period').all()
    
    return [
        {
            "period": str(trend.period),
            "state": trend.state,
            "conflict_type": trend.conflict_type,
            "incidents": trend.incidents,
            "fatalities": trend.fatalities or 0
        }
        for trend in trends
    ]


@router.get("/correlation/poverty")
async def get_poverty_conflict_correlation(
    state: Optional[str] = Query(None),
    current_user: User = Depends(require_role("analyst")),
    db: Session = Depends(get_db)
):
    """Analyze correlation between poverty indicators and conflict"""
    
    # This is a placeholder - would need poverty data table
    # For now, return mock correlation analysis
    return {
        "correlation_coefficient": 0.67,
        "p_value": 0.002,
        "interpretation": "Moderate positive correlation between poverty rate and conflict incidents",
        "data_points": 774,  # Number of LGAs
        "confidence_interval": {
            "lower": 0.45,
            "upper": 0.82
        }
    }


@router.get("/archetypes")
async def get_conflict_archetypes(
    current_user: User = Depends(require_role("analyst")),
    db: Session = Depends(get_db)
):
    """Get statistics by conflict type.
    
    **Requires:** Analyst or Admin role
    """
    
    conflict_types = db.query(
        ConflictEvent.conflict_type,
        func.count(ConflictEvent.id).label('incidents'),
        func.sum(ConflictEvent.fatalities).label('fatalities')
    ).filter(
        ConflictEvent.conflict_type.isnot(None)
    ).group_by(ConflictEvent.conflict_type).order_by(func.count(ConflictEvent.id).desc()).all()
    
    return [
        {
            "conflict_type": ct.conflict_type,
            "incidents": ct.incidents,
            "fatalities": ct.fatalities or 0
        }
        for ct in conflict_types
    ]


def calculate_risk_level(incidents: int, fatalities: int) -> str:
    """Calculate risk level based on incident count and fatalities"""
    if incidents >= 20 or fatalities >= 50:
        return "very_high"
    elif incidents >= 10 or fatalities >= 20:
        return "high"
    elif incidents >= 5 or fatalities >= 10:
        return "medium"
    else:
        return "low"


@router.get("/dashboard-summary")
async def get_dashboard_summary(
    db: Session = Depends(get_db)
):
    """Get dashboard summary statistics with period comparisons.
    
    **Public endpoint** - No authentication required for basic statistics.
    """
    
    # Date ranges for current and previous periods (30 days)
    now = datetime.now().date()
    thirty_days_ago = now - timedelta(days=30)
    sixty_days_ago = now - timedelta(days=60)
    
    # Current period (last 30 days)
    current_period_incidents = db.query(ConflictEvent).filter(
        ConflictEvent.event_date >= thirty_days_ago
    ).count()
    
    current_period_fatalities = db.query(
        func.sum(ConflictEvent.fatalities)
    ).filter(
        ConflictEvent.event_date >= thirty_days_ago
    ).scalar() or 0
    
    # Previous period (30-60 days ago)
    previous_period_incidents = db.query(ConflictEvent).filter(
        ConflictEvent.event_date >= sixty_days_ago,
        ConflictEvent.event_date < thirty_days_ago
    ).count()
    
    previous_period_fatalities = db.query(
        func.sum(ConflictEvent.fatalities)
    ).filter(
        ConflictEvent.event_date >= sixty_days_ago,
        ConflictEvent.event_date < thirty_days_ago
    ).scalar() or 0
    
    # Calculate percentage changes
    incidents_change = 0
    if previous_period_incidents > 0:
        incidents_change = ((current_period_incidents - previous_period_incidents) / previous_period_incidents) * 100
    
    fatalities_change = 0
    if previous_period_fatalities > 0:
        fatalities_change = ((current_period_fatalities - previous_period_fatalities) / previous_period_fatalities) * 100
    
    # Active hotspots (LGAs with 5+ incidents in last 30 days)
    hotspot_count = db.query(
        ConflictEvent.state,
        ConflictEvent.lga
    ).filter(
        ConflictEvent.event_date >= thirty_days_ago
    ).group_by(
        ConflictEvent.state, ConflictEvent.lga
    ).having(
        func.count(ConflictEvent.id) >= 5
    ).count()
    
    # Previous period hotspots for comparison
    previous_hotspot_count = db.query(
        ConflictEvent.state,
        ConflictEvent.lga
    ).filter(
        ConflictEvent.event_date >= sixty_days_ago,
        ConflictEvent.event_date < thirty_days_ago
    ).group_by(
        ConflictEvent.state, ConflictEvent.lga
    ).having(
        func.count(ConflictEvent.id) >= 5
    ).count()
    
    hotspots_change = 0
    if previous_hotspot_count > 0:
        hotspots_change = ((hotspot_count - previous_hotspot_count) / previous_hotspot_count) * 100
    
    # States affected in last 30 days
    states_affected = db.query(ConflictEvent.state).filter(
        ConflictEvent.event_date >= thirty_days_ago
    ).distinct().count()
    
    # Total states in Nigeria
    total_states = 36
    
    # Last updated
    latest_event = db.query(ConflictEvent.event_date).order_by(
        ConflictEvent.event_date.desc()
    ).first()
    
    last_updated = latest_event[0].isoformat() if latest_event else now.isoformat()
    
    return {
        "totalIncidents": current_period_incidents,
        "totalIncidentsChange": round(incidents_change, 1),
        "fatalities": int(current_period_fatalities),
        "fatalitiesChange": round(fatalities_change, 1),
        "activeHotspots": hotspot_count,
        "activeHotspotsChange": round(hotspots_change, 1),
        "statesAffected": states_affected,
        "totalStates": total_states,
        "statesAffectedChange": 0,
        "lastUpdated": last_updated
    }
