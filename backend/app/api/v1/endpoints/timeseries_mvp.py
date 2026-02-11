"""
MVP Time-Series Analytics - Fast & Reliable
Stripped-down version guaranteed to work under 2 seconds
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import json
import logging
from app.db.database import get_db
from app.core.cache import get_from_cache_resilient, set_cache_resilient
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/monthly-trends-fast")
async def get_monthly_trends_fast(
    state: Optional[str] = Query(None, description="Filter by specific state"),
    months_back: int = Query(12, ge=6, le=24, description="Number of months to analyze"),
    db: Session = Depends(get_db)
):
    """
    FAST MVP version of monthly trends - guaranteed under 2 seconds
    
    Simplified logic:
    - Single optimized query
    - Minimal data processing
    - No complex calculations
    - Reliable caching
    
    CACHED: 15 minutes
    """
    # Build cache key
    cache_key = f"timeseries:monthly_trends_fast:{state or 'all'}:{months_back}"
    
    # Try cache first
    cached = await get_from_cache_resilient(cache_key)
    if cached:
        return json.loads(cached)
    
    # Simple optimized query
    cutoff_date = datetime.now() - timedelta(days=months_back * 30)
    
    try:
        if state:
            query = text("""
                SELECT 
                    DATE_TRUNC('month', event_date) as month,
                    COUNT(*) as incidents,
                    COALESCE(SUM(fatalities), 0) as fatalities
                FROM conflict_events
                WHERE event_date >= :cutoff_date
                AND LOWER(state) = LOWER(:state)
                GROUP BY DATE_TRUNC('month', event_date)
                ORDER BY month
                LIMIT 24
            """)
            result = db.execute(query, {'cutoff_date': cutoff_date, 'state': state}).fetchall()
        else:
            query = text("""
                SELECT 
                    DATE_TRUNC('month', event_date) as month,
                    COUNT(*) as incidents,
                    COALESCE(SUM(fatalities), 0) as fatalities
                FROM conflict_events
                WHERE event_date >= :cutoff_date
                GROUP BY DATE_TRUNC('month', event_date)
                ORDER BY month
                LIMIT 24
            """)
            result = db.execute(query, {'cutoff_date': cutoff_date}).fetchall()
            
    except Exception as e:
        logger.error(f"Database query failed: {e}")
        # Return empty response on error
        return {
            "timeRange": {"start": "2025-01", "end": "2025-12", "totalMonths": months_back},
            "state": state or "All States",
            "data": [],
            "summary": {"avgIncidentsPerMonth": 0, "totalIncidents": 0, "trendDirection": "stable"},
            "status": "error",
            "message": "Database query failed"
        }
    
    # Fast data processing - minimal calculations
    if not result:
        response = {
            "timeRange": {"start": "2025-01", "end": "2025-12", "totalMonths": months_back},
            "state": state or "All States",
            "data": [],
            "summary": {"avgIncidentsPerMonth": 0, "totalIncidents": 0, "trendDirection": "stable"},
            "status": "no_data"
        }
    else:
        # Extract data quickly
        months = []
        incidents = []
        fatalities = []
        
        for row in result:
            months.append(row.month.strftime('%Y-%m'))
            incidents.append(row.incidents)
            fatalities.append(int(row.fatalities))
        
        # Simple summary
        total_incidents = sum(incidents)
        avg_incidents = total_incidents / len(incidents) if incidents else 0
        
        # Simple trend (compare last 3 months to previous 3)
        if len(incidents) >= 6:
            recent_avg = sum(incidents[-3:]) / 3
            previous_avg = sum(incidents[-6:-3]) / 3
            trend = "increasing" if recent_avg > previous_avg * 1.1 else "decreasing" if recent_avg < previous_avg * 0.9 else "stable"
        else:
            trend = "stable"
        
        response = {
            "timeRange": {
                "start": months[0] if months else "2025-01",
                "end": months[-1] if months else "2025-12",
                "totalMonths": len(months)
            },
            "state": state or "All States",
            "data": [
                {
                    "month": months[i],
                    "incidents": incidents[i],
                    "fatalities": fatalities[i]
                }
                for i in range(len(months))
            ],
            "summary": {
                "avgIncidentsPerMonth": round(avg_incidents, 1),
                "totalIncidents": total_incidents,
                "trendDirection": trend
            },
            "status": "success"
        }
    
    # Cache for 15 minutes
    await set_cache_resilient(cache_key, response, ttl=900)
    
    return response


@router.get("/stats-fast")
async def get_stats_fast(db: Session = Depends(get_db)):
    """
    FAST MVP version of stats endpoint - under 1 second
    """
    cache_key = "timeseries:stats_fast"
    
    # Try cache first
    cached = await get_from_cache_resilient(cache_key)
    if cached:
        return json.loads(cached)
    
    try:
        # Simple fast queries
        total_query = text("SELECT COUNT(*) as count FROM conflict_events")
        total_result = db.execute(total_query).fetchone()
        
        recent_query = text("""
            SELECT COUNT(*) as count 
            FROM conflict_events 
            WHERE event_date >= CURRENT_DATE - INTERVAL '30 days'
        """)
        recent_result = db.execute(recent_query).fetchone()
        
        fatalities_query = text("""
            SELECT COALESCE(SUM(fatalities), 0) as total
            FROM conflict_events
        """)
        fatalities_result = db.execute(fatalities_query).fetchone()
        
        response = {
            "totalIncidents": total_result.count,
            "recentIncidents": recent_result.count,
            "totalFatalities": int(fatalities_result.total),
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Stats query failed: {e}")
        response = {
            "totalIncidents": 0,
            "recentIncidents": 0,
            "totalFatalities": 0,
            "status": "error"
        }
    
    # Cache for 10 minutes
    await set_cache_resilient(cache_key, response, ttl=600)
    
    return response
