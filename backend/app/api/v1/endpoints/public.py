from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.exc import OperationalError, DisconnectionError
from datetime import datetime, timedelta
from typing import List
import time
import logging

from app.db.database import get_db
from app.models.conflict import Conflict
from app.models.reference import State, LGA, ConflictType

router = APIRouter()
logger = logging.getLogger(__name__)


def retry_database_operation(func, max_retries=3, delay=1):
    """Retry database operations with exponential backoff"""
    for attempt in range(max_retries):
        try:
            return func()
        except (OperationalError, DisconnectionError) as e:
            if attempt == max_retries - 1:
                logger.error(f"Database operation failed after {max_retries} attempts: {e}")
                raise HTTPException(
                    status_code=503,
                    detail="Database temporarily unavailable. Please try again in a moment."
                )
            else:
                wait_time = delay * (2 ** attempt)
                logger.warning(f"Database connection error (attempt {attempt + 1}), retrying in {wait_time}s: {e}")
                time.sleep(wait_time)


@router.get("/landing-stats")
async def get_landing_stats(db: Session = Depends(get_db)):
    """Get public landing page statistics.
    
    **Public endpoint** - No authentication required.
    Returns aggregate conflict statistics for the landing page.
    """
    
    def get_stats():
        # Date ranges
        now = datetime.now().date()
        thirty_days_ago = now - timedelta(days=30)
        six_months_ago = now - timedelta(days=180)
        
        # Total incidents in last 30 days
        total_incidents_30d = db.query(Conflict).filter(
            Conflict.incidence_date >= thirty_days_ago
        ).count()
        
        # Total fatalities in last 30 days (civilian deaths)
        total_fatalities_30d = db.query(
            func.sum(Conflict.civilian_death_unknown)
        ).filter(
            Conflict.incidence_date >= thirty_days_ago
        ).scalar() or 0
        
        # Active hotspots (LGAs with >=5 incidents in last 30 days)
        hotspots = db.query(
            Conflict.lga_id
        ).filter(
            Conflict.incidence_date >= thirty_days_ago,
            Conflict.lga_id.isnot(None)
        ).group_by(
            Conflict.lga_id
        ).having(
            func.count(Conflict.id) >= 5
        ).count()
        
        # States affected in last 30 days
        states_affected = db.query(
            Conflict.state_id
        ).filter(
            Conflict.incidence_date >= thirty_days_ago,
            Conflict.state_id.isnot(None)
        ).distinct().count()
        
        # Timeline sparkline (last 6 months, monthly aggregates)
        timeline_data = []
        for i in range(6, 0, -1):
            month_start = now - timedelta(days=i * 30)
            month_end = now - timedelta(days=(i - 1) * 30)
            
            count = db.query(Conflict).filter(
                Conflict.incidence_date >= month_start,
                Conflict.incidence_date < month_end
            ).count()
            
            timeline_data.append(count)
        
        # Top 5 affected states by incident count
        top_states_query = db.query(
            State.name,
            func.count(Conflict.id).label('incidents'),
            func.sum(Conflict.civilian_death_unknown).label('fatalities')
        ).join(
            State, Conflict.state_id == State.id
        ).filter(
            Conflict.incidence_date >= thirty_days_ago
        ).group_by(
            State.name
        ).order_by(
            func.count(Conflict.id).desc()
        ).limit(5).all()
        
        top_states = []
        for state_data in top_states_query:
            incidents = state_data.incidents
            # Determine severity based on incident count
            if incidents >= 20:
                severity = "high"
            elif incidents >= 10:
                severity = "medium"
            else:
                severity = "low"
            
            top_states.append({
                "name": state_data.state,
                "incidents": incidents,
                "fatalities": state_data.fatalities or 0,
                "severity": severity
            })
        
        return {
            "total_incidents_30d": total_incidents_30d,
            "total_fatalities_30d": int(total_fatalities_30d),
            "active_hotspots": hotspots,
            "states_affected": states_affected,
            "last_updated": datetime.now().isoformat(),
            "timeline_sparkline": timeline_data,
            "top_states": top_states
        }
    
    # Execute with retry logic
    return retry_database_operation(get_stats)


@router.get("/recent-conflicts")
async def get_recent_conflicts(
    limit: int = 5,
    db: Session = Depends(get_db)
):
    """Get recent conflict events for public preview.
    
    **Public endpoint** - No authentication required.
    Returns the most recent conflict incidents (limited to 10 max).
    """
    
    def get_conflicts():
        # Limit to max 10 for security
        safe_limit = min(limit, 10)
        
        conflicts = db.query(Conflict).order_by(
            Conflict.incidence_date.desc()
        ).limit(safe_limit).all()
        
        return [
            {
                "id": str(conflict.id),
                "state": conflict.state_rel.name if conflict.state_rel else None,
                "lga": conflict.lga_rel.name if conflict.lga_rel else None,
                "event_type": conflict.conflict_type_rel.title if conflict.conflict_type_rel else None,
                "fatalities": conflict.civilian_death_unknown or 0,
                "injuries": conflict.injured_unknown or 0,
                "event_date": conflict.incidence_date.isoformat() if conflict.incidence_date else None,
                "verified": True,
                "source": conflict.source_url
            }
            for conflict in conflicts
        ]
    
    # Execute with retry logic
    return retry_database_operation(get_conflicts)
