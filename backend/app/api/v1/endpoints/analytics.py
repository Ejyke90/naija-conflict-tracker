from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, timedelta

from app.db.database import get_db
from app.models.conflict import Conflict

router = APIRouter()


@router.get("/hotspots")
async def get_conflict_hotspots(
    radius_km: int = Query(50, ge=1, le=500),
    min_incidents: int = Query(5, ge=1),
    db: Session = Depends(get_db)
):
    """Get conflict hotspots - areas with high concentration of incidents"""
    
    # Query for high-conflict LGAs in last 6 months
    six_months_ago = datetime.now() - timedelta(days=180)
    
    hotspots = db.query(
        Conflict.state,
        Conflict.lga,
        func.count(Conflict.id).label('incident_count'),
        func.sum(Conflict.fatalities_male + Conflict.fatalities_female + Conflict.fatalities_unknown).label('total_fatalities'),
        func.sum(Conflict.kidnapped_male + Conflict.kidnapped_female + Conflict.kidnapped_unknown).label('total_kidnapped'),
        func.avg(Conflict.confidence_score).label('avg_confidence')
    ).filter(
        Conflict.event_date >= six_months_ago
    ).group_by(
        Conflict.state, Conflict.lga
    ).having(
        func.count(Conflict.id) >= min_incidents
    ).order_by(
        func.count(Conflict.id).desc()
    ).all()
    
    return [
        {
            "state": hotspot.state,
            "lga": hotspot.lga,
            "incident_count": hotspot.incident_count,
            "total_fatalities": hotspot.total_fatalities or 0,
            "total_kidnapped": hotspot.total_kidnapped or 0,
            "avg_confidence": float(hotspot.avg_confidence or 0),
            "risk_level": calculate_risk_level(hotspot.incident_count, hotspot.total_fatalities or 0)
        }
        for hotspot in hotspots
    ]


@router.get("/trends")
async def get_conflict_trends(
    period: str = Query("monthly", regex="^(daily|weekly|monthly)$"),
    months: int = Query(12, ge=1, le=60),
    db: Session = Depends(get_db)
):
    """Get conflict trends over time"""
    
    start_date = datetime.now() - timedelta(days=months * 30)
    
    if period == "daily":
        date_trunc = func.date_trunc('day', Conflict.event_date)
    elif period == "weekly":
        date_trunc = func.date_trunc('week', Conflict.event_date)
    else:  # monthly
        date_trunc = func.date_trunc('month', Conflict.event_date)
    
    trends = db.query(
        date_trunc.label('period'),
        Conflict.state,
        Conflict.event_type,
        func.count(Conflict.id).label('incidents'),
        func.sum(Conflict.fatalities_male + Conflict.fatalities_female + Conflict.fatalities_unknown).label('fatalities')
    ).filter(
        Conflict.event_date >= start_date
    ).group_by(
        'period', Conflict.state, Conflict.event_type
    ).order_by('period').all()
    
    return [
        {
            "period": str(trend.period),
            "state": trend.state,
            "event_type": trend.event_type,
            "incidents": trend.incidents,
            "fatalities": trend.fatalities or 0
        }
        for trend in trends
    ]


@router.get("/correlation/poverty")
async def get_poverty_conflict_correlation(
    state: Optional[str] = Query(None),
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
    db: Session = Depends(get_db)
):
    """Get statistics by conflict archetype"""
    
    archetypes = db.query(
        Conflict.archetype,
        func.count(Conflict.id).label('incidents'),
        func.sum(Conflict.fatalities_male + Conflict.fatalities_female + Conflict.fatalities_unknown).label('fatalities'),
        func.avg(Conflict.confidence_score).label('avg_confidence')
    ).filter(
        Conflict.archetype.isnot(None)
    ).group_by(Conflict.archetype).order_by(func.count(Conflict.id).desc()).all()
    
    return [
        {
            "archetype": archetype.archetype,
            "incidents": archetype.incidents,
            "fatalities": archetype.fatalities or 0,
            "avg_confidence": float(archetype.avg_confidence or 0)
        }
        for archetype in archetypes
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
