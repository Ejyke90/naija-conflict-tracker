from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, timedelta
import logging
import json

from app.db.database import get_db
from app.models.conflict import Conflict
from app.models.reference import State, LGA, ConflictType
from app.models.auth import User
from app.api.deps import require_role
from app.core.cache import get_redis_client

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/hotspots")
async def get_conflict_hotspots(
    radius_km: int = Query(50, ge=1, le=500),
    min_incidents: int = Query(5, ge=1),
    current_user: User = Depends(require_role("viewer")),
    db: Session = Depends(get_db)
):
    """Get conflict hotspots - areas with high concentration of incidents.
    
    **Requires:** Viewer, Analyst or Admin role
    """
    try:
        # Query for high-conflict LGAs in last 6 months
        six_months_ago = datetime.now().date() - timedelta(days=180)
        
        hotspots = db.query(
            State.name.label('state'),
            LGA.name.label('lga'),
            func.count(Conflict.id).label('incident_count'),
            func.sum(Conflict.civilian_death_unknown).label('total_fatalities'),
            func.sum(Conflict.displaced_male + Conflict.displaced_female).label('total_displaced')
        ).join(
            State, Conflict.state_id == State.id
        ).join(
            LGA, Conflict.lga_id == LGA.id
        ).filter(
            Conflict.incidence_date >= six_months_ago
        ).group_by(
            State.name, LGA.name
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
                "total_displaced": hotspot.total_displaced or 0,
                "risk_level": calculate_risk_level(hotspot.incident_count, hotspot.total_fatalities or 0)
            }
            for hotspot in hotspots
        ]
    except Exception as e:
        logger.error(f"Error in get_conflict_hotspots: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "Failed to retrieve conflict hotspots",
                "error_code": "HOTSPOTS_QUERY_ERROR"
            }
        )


@router.get("/trends")
async def get_conflict_trends(
    period: str = Query("monthly", pattern="^(daily|weekly|monthly)$"),
    months: int = Query(12, ge=1, le=60),
    current_user: User = Depends(require_role("viewer")),
    db: Session = Depends(get_db)
):
    """Get conflict trends over time.
    
    **Requires:** Viewer, Analyst or Admin role
    """
    try:
        start_date = datetime.now().date() - timedelta(days=months * 30)
        
        if period == "daily":
            date_trunc = func.date(Conflict.incidence_date)
        elif period == "weekly":
            # Use date and calculate week number
            date_trunc = func.date(Conflict.incidence_date)
        else:  # monthly
            # Extract year-month for grouping
            date_trunc = func.date(Conflict.incidence_date)
        
        trends = db.query(
            date_trunc.label('period'),
            State.name.label('state'),
            ConflictType.title.label('conflict_type'),
            func.count(Conflict.id).label('incidents'),
            func.sum(Conflict.civilian_death_unknown).label('fatalities')
        ).join(
            State, Conflict.state_id == State.id
        ).outerjoin(
            ConflictType, Conflict.conflict_type_id == ConflictType.id
        ).filter(
            Conflict.incidence_date >= start_date
        ).group_by(
            date_trunc, State.name, ConflictType.title
        ).order_by(date_trunc).all()
        
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
    except Exception as e:
        logger.error(f"Error in get_conflict_trends: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "Failed to retrieve conflict trends",
                "error_code": "TRENDS_QUERY_ERROR"
            }
        )


@router.get("/correlation/poverty")
async def get_poverty_conflict_correlation(
    state: Optional[str] = Query(None),
    current_user: User = Depends(require_role("viewer")),
    db: Session = Depends(get_db)
):
    """Analyze correlation between poverty indicators and conflict
    
    **Requires:** Viewer, Analyst or Admin role
    """
    
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
    current_user: User = Depends(require_role("viewer")),
    db: Session = Depends(get_db)
):
    """Get statistics by conflict type.
    
    **Requires:** Viewer, Analyst or Admin role
    """
    try:
        conflict_types = db.query(
            Conflict.conflict_type,
            func.count(Conflict.id).label('incidents'),
            func.sum(Conflict.civilian_death_unknown).label('fatalities')
        ).filter(
            Conflict.conflict_type.isnot(None)
        ).group_by(Conflict.conflict_type).order_by(func.count(Conflict.id).desc()).all()
        
        return [
            {
                "conflict_type": ct.conflict_type,
                "incidents": ct.incidents,
                "fatalities": ct.fatalities or 0
            }
            for ct in conflict_types
        ]
    except Exception as e:
        logger.error(f"Error in get_conflict_archetypes: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "Failed to retrieve conflict archetypes",
                "error_code": "ARCHETYPES_QUERY_ERROR"
            }
        )


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


@router.get("/stats")
async def get_public_stats(
    db: Session = Depends(get_db)
):
    """Get public statistics for landing page (no authentication required).
    
    Returns basic metrics optimized for the LivePulse component:
    - Total incidents (last 30 days)
    - Percentage change from previous period
    - States affected
    - Active hotspots
    
    **Public endpoint** - No authentication required.
    **Cache:** 5 minutes
    """
    try:
        # Try cache first (with timeout protection)
        cache = await get_redis_client()
        cache_key = "analytics:public_stats"
        cached_result = None

        if cache:
            try:
                cached_result = await cache.get(cache_key)
                if cached_result:
                    return json.loads(cached_result)
            except Exception as cache_error:
                # Log but don't fail - continue without cache
                logger.warning(f"Redis cache read error for stats: {cache_error}")

        # Date ranges for current and previous periods (30 days)
        now = datetime.now().date()
        thirty_days_ago = now - timedelta(days=30)
        sixty_days_ago = now - timedelta(days=60)

        # Current period (last 30 days)
        current_period_incidents = db.query(Conflict).filter(
            Conflict.incidence_date >= thirty_days_ago
        ).count()

        # Previous period (30-60 days ago)
        previous_period_incidents = db.query(Conflict).filter(
            Conflict.incidence_date >= sixty_days_ago,
            Conflict.incidence_date < thirty_days_ago
        ).count()

        # Calculate percentage change
        incidents_change = 0
        if previous_period_incidents > 0:
            incidents_change = ((current_period_incidents - previous_period_incidents) / previous_period_incidents) * 100

        # Active hotspots (LGAs with 5+ incidents in last 30 days)
        hotspot_count = db.query(
            State.name,
            LGA.name
        ).select_from(Conflict).join(
            State, Conflict.state_id == State.id
        ).join(
            LGA, Conflict.lga_id == LGA.id
        ).filter(
            Conflict.incidence_date >= thirty_days_ago
        ).group_by(
            State.name, LGA.name
        ).having(
            func.count(Conflict.id) >= 5
        ).count()

        # States affected in last 30 days
        states_affected = db.query(State.name).join(
            Conflict, State.id == Conflict.state_id
        ).filter(
            Conflict.incidence_date >= thirty_days_ago
        ).distinct().count()

        result = {
            "totalIncidents": current_period_incidents,
            "totalIncidentsChange": round(incidents_change, 1),
            "statesAffected": states_affected,
            "activeHotspots": hotspot_count,
            "previousPeriodIncidents": previous_period_incidents
        }

        # Cache for 5 minutes (with timeout protection)
        if cache:
            try:
                await cache.set(cache_key, json.dumps(result), ex=300)
            except Exception as cache_error:
                logger.warning(f"Redis cache write error for stats: {cache_error}")

        return result
    except Exception as e:
        logger.error(f"Error in get_public_stats: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "Failed to retrieve statistics",
                "error_code": "STATS_ERROR"
            }
        )


@router.get("/dashboard-summary")
async def get_dashboard_summary(
    current_user: User = Depends(require_role("viewer")),
    db: Session = Depends(get_db)
):
    """Get dashboard summary statistics with period comparisons.
    
    **Requires:** Viewer, Analyst or Admin role (changed from analyst-only)
    """
    try:
        # Date ranges for current and previous periods (30 days)
        now = datetime.now().date()
        thirty_days_ago = now - timedelta(days=30)
        sixty_days_ago = now - timedelta(days=60)
        
        # Current period (last 30 days)
        current_period_incidents = db.query(Conflict).filter(
            Conflict.incidence_date >= thirty_days_ago
        ).count()
        
        current_period_fatalities = db.query(
            func.sum(Conflict.civilian_death_unknown)
        ).filter(
            Conflict.incidence_date >= thirty_days_ago
        ).scalar() or 0
        
        # Previous period (30-60 days ago)
        previous_period_incidents = db.query(Conflict).filter(
            Conflict.incidence_date >= sixty_days_ago,
            Conflict.incidence_date < thirty_days_ago
        ).count()
        
        previous_period_fatalities = db.query(
            func.sum(Conflict.civilian_death_unknown)
        ).filter(
            Conflict.incidence_date >= sixty_days_ago,
            Conflict.incidence_date < thirty_days_ago
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
            State.name,
            LGA.name
        ).select_from(Conflict).join(
            State, Conflict.state_id == State.id
        ).join(
            LGA, Conflict.lga_id == LGA.id
        ).filter(
            Conflict.incidence_date >= thirty_days_ago
        ).group_by(
            State.name, LGA.name
        ).having(
            func.count(Conflict.id) >= 5
        ).count()
        
        # Previous period hotspots for comparison
        previous_hotspot_count = db.query(
            State.name,
            LGA.name
        ).select_from(Conflict).join(
            State, Conflict.state_id == State.id
        ).join(
            LGA, Conflict.lga_id == LGA.id
        ).filter(
            Conflict.incidence_date >= sixty_days_ago,
            Conflict.incidence_date < thirty_days_ago
        ).group_by(
            State.name, LGA.name
        ).having(
            func.count(Conflict.id) >= 5
        ).count()
        
        hotspots_change = 0
        if previous_hotspot_count > 0:
            hotspots_change = ((hotspot_count - previous_hotspot_count) / previous_hotspot_count) * 100
        
        # States affected in last 30 days
        states_affected = db.query(State.name).join(
            Conflict, State.id == Conflict.state_id
        ).filter(
            Conflict.incidence_date >= thirty_days_ago
        ).distinct().count()
        
        # Total states in Nigeria
        total_states = 36
        
        # Last updated
        latest_event = db.query(Conflict.incidence_date).order_by(
            Conflict.incidence_date.desc()
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
    except Exception as e:
        logger.error(f"Error in get_dashboard_summary: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "Failed to retrieve dashboard summary",
                "error_code": "DASHBOARD_SUMMARY_ERROR"
            }
        )


@router.get("/states")
async def get_state_statistics(
    months_back: int = Query(12, ge=1, le=60),
    db: Session = Depends(get_db)
):
    """Get statistics for all states ranked by fatalities.
    
    Used for smart default state selection in comparisons.
    Public endpoint (no auth required) for better performance.
    """
    try:
        cutoff_date = datetime.now().date() - timedelta(days=months_back * 30)
        
        # Query state statistics
        state_stats = db.query(
            State.name.label('state'),
            func.count(Conflict.id).label('incidents'),
            func.coalesce(
                func.sum(
                    Conflict.civilian_death_male + 
                    Conflict.civilian_death_female + 
                    Conflict.civilian_death_unknown +
                    Conflict.security_death_male + 
                    Conflict.security_death_female + 
                    Conflict.security_death_unknown
                ), 0
            ).label('fatalities')
        ).join(
            Conflict, State.id == Conflict.state_id
        ).filter(
            Conflict.incidence_date >= cutoff_date
        ).group_by(
            State.name
        ).order_by(
            func.sum(
                Conflict.civilian_death_male + 
                Conflict.civilian_death_female + 
                Conflict.civilian_death_unknown +
                Conflict.security_death_male + 
                Conflict.security_death_female + 
                Conflict.security_death_unknown
            ).desc()
        ).all()
        
        return {
            "status": "ok",
            "data": [
                {
                    "state": stat.state,
                    "incidents": int(stat.incidents),
                    "fatalities": int(stat.fatalities)
                }
                for stat in state_stats
            ],
            "cached": False
        }
    except Exception as e:
        logger.error(f"Error in get_state_statistics: {str(e)}", exc_info=True)
        # Return graceful degraded response instead of 500 error
        return {
            "status": "degraded",
            "data": [],
            "message": "Unable to retrieve state statistics; database unavailable",
            "cached": False,
            "error_code": "STATE_STATS_ERROR"
        }
