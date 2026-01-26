from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.exc import OperationalError, DisconnectionError
from datetime import datetime, timedelta
from typing import List
import time
import logging

from app.db.database import get_db
from app.models.conflict import ConflictEvent

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
        total_incidents_30d = db.query(ConflictEvent).filter(
            ConflictEvent.event_date >= thirty_days_ago
        ).count()
        
        # Total fatalities in last 30 days
        total_fatalities_30d = db.query(
            func.sum(ConflictEvent.fatalities)
        ).filter(
            ConflictEvent.event_date >= thirty_days_ago
        ).scalar() or 0
        
        # Active hotspots (LGAs with >=5 incidents in last 30 days)
        hotspots = db.query(
            ConflictEvent.lga
        ).filter(
            ConflictEvent.event_date >= thirty_days_ago,
            ConflictEvent.lga.isnot(None)
        ).group_by(
            ConflictEvent.lga
        ).having(
            func.count(ConflictEvent.id) >= 5
        ).count()
        
        # States affected in last 30 days
# States affected in last 30 days
        states_affected = db.query(
            ConflictEvent.state
        ).filter(
            ConflictEvent.event_date >= thirty_days_ago,
            ConflictEvent.state.isnot(None)
        ).distinct().count()
        
        # Timeline sparkline (last 6 months, monthly aggregates)
        timeline_data = []
        for i in range(6, 0, -1):
            month_start = now - timedelta(days=i * 30)
            month_end = now - timedelta(days=(i - 1) * 30)
            
            count = db.query(ConflictEvent).filter(
                ConflictEvent.event_date >= month_start,
                ConflictEvent.event_date < month_end
            ).count()
            
            timeline_data.append(count)
        
        # Top 5 affected states by incident count
        top_states_query = db.query(
            ConflictEvent.state,
            func.count(ConflictEvent.id).label('incidents'),
            func.sum(ConflictEvent.fatalities).label('fatalities')
        ).filter(
            ConflictEvent.event_date >= thirty_days_ago,
            ConflictEvent.state.isnot(None)
        ).group_by(
            ConflictEvent.state
        ).order_by(
            func.count(ConflictEvent.id).desc()
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
