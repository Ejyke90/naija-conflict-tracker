"""
Minimal dashboard API without model dependencies
"""

from fastapi import APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, timedelta

from app.db.database import get_db

router = APIRouter(prefix="/api/minimal", tags=["minimal"])

@router.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Get statistics using raw SQL"""
    try:
        cutoff_date = datetime.now() - timedelta(days=30)
        
        # Total incidents
        result = db.execute(
            text("SELECT COUNT(*) FROM conflicts WHERE event_date >= :cutoff_date"),
            {"cutoff_date": cutoff_date}
        ).scalar()
        total_incidents = result or 0
        
        # Total casualties
        result = db.execute(
            text("""
                SELECT 
                    SUM(fatalities_male + fatalities_female + fatalities_unknown) as fatalities,
                    SUM(injured_male + injured_female + injured_unknown) as injuries
                FROM conflicts 
                WHERE event_date >= :cutoff_date
            """),
            {"cutoff_date": cutoff_date}
        ).first()
        total_fatalities = result.fatalities or 0
        total_injuries = result.injuries or 0
        
        # States affected
        result = db.execute(
            text("SELECT COUNT(DISTINCT state) FROM conflicts WHERE event_date >= :cutoff_date"),
            {"cutoff_date": cutoff_date}
        ).scalar()
        states_affected = result or 0
        
        return {
            "total_incidents": total_incidents,
            "total_fatalities": total_fatalities,
            "total_injuries": total_injuries,
            "total_casualties": total_fatalities + total_injuries,
            "states_affected": states_affected,
            "period_days": 30,
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "total_incidents": 0,
            "total_fatalities": 0,
            "total_injuries": 0,
            "total_casualties": 0,
            "states_affected": 0,
            "period_days": 30,
            "last_updated": datetime.now().isoformat()
        }

@router.get("/recent")
async def get_recent(db: Session = Depends(get_db)):
    """Get recent incidents"""
    try:
        cutoff_date = datetime.now() - timedelta(days=7)
        
        result = db.execute(
            text("""
                SELECT 
                    event_date, state, lga, community, 
                    archetype, perpetrator_group, description,
                    fatalities_male, fatalities_female, fatalities_unknown
                FROM conflicts 
                WHERE event_date >= :cutoff_date 
                ORDER BY event_date DESC 
                LIMIT 10
            """),
            {"cutoff_date": cutoff_date}
        ).fetchall()
        
        incidents = []
        for row in result:
            incidents.append({
                "date": row[0].strftime("%Y-%m-%d"),
                "location": f"{row[1]}, {row[2] or ''}",
                "type": row[4] or "Unknown",
                "fatalities": (row[5] or 0) + (row[6] or 0) + (row[7] or 0),
                "perpetrator": row[8] or "Unknown",
                "description": row[9] or ""
            })
        
        return {
            "incidents": incidents,
            "showing": len(incidents),
            "period_days": 7
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "incidents": [],
            "showing": 0,
            "period_days": 7
        }
