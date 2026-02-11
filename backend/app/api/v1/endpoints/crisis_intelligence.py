"""
Multi-Dimensional Crisis Intelligence Dashboard API - Simplified Version
Works directly with conflict_events view for immediate deployment
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel
import json

from app.db.database import get_db
from app.api.deps import get_optional_user
from app.core.cache import get_redis_client

router = APIRouter()

# Pydantic models for structured responses
class CrisisMetrics(BaseModel):
    incidents: int
    fatalities: int
    displaced: int
    injuries: int
    crisis_index_score: float
    risk_level: str

class StateHotspot(BaseModel):
    state: str
    total_incidents: int
    total_fatalities: int
    total_displaced: int
    crisis_index_score: float
    risk_level: str
    recent_incidents: int
    recent_fatalities: int

class ActorThreat(BaseModel):
    actor: str
    actor_type: str
    event_type: str
    incidents: int
    total_fatalities: int
    total_displaced: int
    threat_score: float
    threat_level: str
    states_affected: int

class CrisisType(BaseModel):
    event_type: str
    conflict_type: str
    total_incidents: int
    total_fatalities: int
    total_displaced: int
    states_affected: int
    trend_direction: str
    recent_incidents: int

class CrisisIntelligenceResponse(BaseModel):
    current_period: CrisisMetrics
    state_hotspots: List[StateHotspot]
    actor_threats: List[ActorThreat]
    crisis_types: List[CrisisType]
    monthly_trends: List[Dict[str, Any]]
    last_updated: str

@router.get("/crisis-intelligence", response_model=CrisisIntelligenceResponse)
async def get_crisis_intelligence(
    months_back: int = Query(12, ge=1, le=24, description="Number of months to analyze"),
    top_states: int = Query(10, ge=5, le=36, description="Number of top states to return"),
    top_actors: int = Query(10, ge=5, le=20, description="Number of top actors to return"),
    db: Session = Depends(get_db),
    current_user = Depends(get_optional_user)
):
    """
    Get comprehensive crisis intelligence data optimized for performance.
    Uses conflict_events view directly with Redis caching.
    """
    try:
        # Try to get from cache first
        cache_key = f"crisis_intelligence_{months_back}_{top_states}_{top_actors}"
        redis_client = await get_redis_client()
        
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return CrisisIntelligenceResponse.model_validate_json(cached_data)
        
        # Generate cutoff date
        cutoff_date = datetime.now().date() - timedelta(days=months_back * 30)
        
        # 1. Current Period Crisis Metrics from conflict_events
        current_metrics_query = db.execute(text("""
            SELECT 
                COUNT(*) as incidents,
                SUM(fatalities) as total_fatalities,
                SUM(displaced_persons) as total_displaced,
                SUM(injuries) as total_injuries,
                (SUM(fatalities) * 3 + SUM(displaced_persons) * 1 + SUM(injuries) * 0.5) as crisis_index_score
            FROM conflict_events 
            WHERE event_date >= :cutoff_date
        """), {"cutoff_date": cutoff_date}).first()
        
        # Calculate risk level
        crisis_score = current_metrics_query.crisis_index_score or 0
        if crisis_score >= 1000:
            risk_level = 'CRITICAL'
        elif crisis_score >= 500:
            risk_level = 'HIGH'
        elif crisis_score >= 200:
            risk_level = 'MEDIUM'
        else:
            risk_level = 'LOW'
        
        # 2. State Hotspots Analysis
        state_hotspots_query = db.execute(text("""
            SELECT 
                state,
                COUNT(*) as total_incidents,
                SUM(fatalities) as total_fatalities,
                SUM(displaced_persons) as total_displaced,
                (SUM(fatalities) * 3 + SUM(displaced_persons) * 1 + SUM(injuries) * 0.5) as crisis_index_score,
                COUNT(*) FILTER (WHERE event_date >= CURRENT_DATE - INTERVAL '30 days') as recent_incidents,
                SUM(fatalities) FILTER (WHERE event_date >= CURRENT_DATE - INTERVAL '30 days') as recent_fatalities
            FROM conflict_events 
            WHERE state IS NOT NULL
            GROUP BY state
            ORDER BY crisis_index_score DESC
            LIMIT :limit
        """), {"limit": top_states}).fetchall()
        
        # 3. Actor Threat Analysis
        actor_threats_query = db.execute(text("""
            SELECT 
                actor1 as actor,
                COALESCE(actor1_type, 'Unknown') as actor_type,
                event_type,
                COUNT(*) as incidents,
                SUM(fatalities) as total_fatalities,
                SUM(displaced_persons) as total_displaced,
                COUNT(DISTINCT state) as states_affected,
                (SUM(fatalities) * 3 + SUM(displaced_persons) * 1 + SUM(injuries) * 0.5) as threat_score
            FROM conflict_events 
            WHERE actor1 IS NOT NULL
            GROUP BY actor1, actor1_type, event_type
            ORDER BY threat_score DESC
            LIMIT :limit
        """), {"limit": top_actors}).fetchall()
        
        # 4. Crisis Type Distribution
        crisis_types_query = db.execute(text("""
            SELECT 
                event_type,
                conflict_type,
                COUNT(*) as total_incidents,
                SUM(fatalities) as total_fatalities,
                SUM(displaced_persons) as total_displaced,
                COUNT(DISTINCT state) as states_affected,
                COUNT(*) FILTER (WHERE event_date >= CURRENT_DATE - INTERVAL '6 months') as recent_incidents,
                COUNT(*) FILTER (WHERE event_date >= CURRENT_DATE - INTERVAL '12 months' AND event_date < CURRENT_DATE - INTERVAL '6 months') as previous_incidents
            FROM conflict_events 
            WHERE event_type IS NOT NULL
            GROUP BY event_type, conflict_type
            ORDER BY total_incidents DESC
        """)).fetchall()
        
        # 5. Monthly Trends
        monthly_trends_query = db.execute(text("""
            SELECT 
                to_char(event_date, 'YYYY-MM') as month,
                COUNT(*) as incidents,
                SUM(fatalities) as fatalities,
                SUM(displaced_persons) as displaced,
                (SUM(fatalities) * 3 + SUM(displaced_persons) * 1 + SUM(injuries) * 0.5) as crisis_score
            FROM conflict_events 
            WHERE event_date >= :cutoff_date
            GROUP BY to_char(event_date, 'YYYY-MM')
            ORDER BY month
        """), {"cutoff_date": cutoff_date}).fetchall()
        
        # Build response
        response = CrisisIntelligenceResponse(
            current_period=CrisisMetrics(
                incidents=current_metrics_query.incidents or 0,
                fatalities=current_metrics_query.total_fatalities or 0,
                displaced=current_metrics_query.total_displaced or 0,
                injuries=current_metrics_query.total_injuries or 0,
                crisis_index_score=float(current_metrics_query.crisis_index_score or 0),
                risk_level=risk_level
            ),
            state_hotspots=[
                StateHotspot(
                    state=row.state,
                    total_incidents=row.total_incidents,
                    total_fatalities=row.total_fatalities or 0,
                    total_displaced=row.total_displaced or 0,
                    crisis_index_score=float(row.crisis_index_score or 0),
                    risk_level='HIGH' if (row.crisis_index_score or 0) >= 100 else 'MEDIUM' if (row.crisis_index_score or 0) >= 50 else 'LOW',
                    recent_incidents=row.recent_incidents or 0,
                    recent_fatalities=row.recent_fatalities or 0
                ) for row in state_hotspots_query
            ],
            actor_threats=[
                ActorThreat(
                    actor=row.actor,
                    actor_type=row.actor_type,
                    event_type=row.event_type,
                    incidents=row.incidents,
                    total_fatalities=row.total_fatalities or 0,
                    total_displaced=row.total_displaced or 0,
                    threat_score=float(row.threat_score or 0),
                    threat_level='CRITICAL' if (row.threat_score or 0) >= 200 else 'HIGH' if (row.threat_score or 0) >= 100 else 'MEDIUM' if (row.threat_score or 0) >= 50 else 'LOW',
                    states_affected=row.states_affected
                ) for row in actor_threats_query
            ],
            crisis_types=[
                CrisisType(
                    event_type=row.event_type,
                    conflict_type=row.conflict_type,
                    total_incidents=row.total_incidents,
                    total_fatalities=row.total_fatalities or 0,
                    total_displaced=row.total_displaced or 0,
                    states_affected=row.states_affected,
                    trend_direction='NEW' if row.previous_incidents == 0 else 'INCREASING' if (row.recent_incidents / row.previous_incidents) > 1.2 else 'DECREASING' if (row.recent_incidents / row.previous_incidents) < 0.8 else 'STABLE',
                    recent_incidents=row.recent_incidents
                ) for row in crisis_types_query
            ],
            monthly_trends=[
                {
                    "month": row.month,
                    "incidents": row.incidents,
                    "fatalities": row.fatalities,
                    "displaced": row.displaced,
                    "crisis_score": float(row.crisis_score or 0)
                } for row in monthly_trends_query
            ],
            last_updated=datetime.now().isoformat()
        )
        
        # Cache the response for 15 minutes (900 seconds)
        await redis_client.setex(cache_key, 900, response.model_dump_json())
        
        return response
        
    except Exception as e:
        print(f"Error in crisis intelligence endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch crisis intelligence: {str(e)}")

@router.post("/refresh-views")
async def refresh_crisis_views(
    db: Session = Depends(get_db),
    current_user = Depends(get_optional_user)
):
    """
    Refresh crisis intelligence cache.
    """
    try:
        redis_client = await get_redis_client()
        # Clear all crisis intelligence cache keys
        cache_keys = await redis_client.keys("crisis_intelligence_*")
        if cache_keys:
            await redis_client.delete(*cache_keys)
        
        return {"message": "Crisis intelligence cache refreshed successfully", "timestamp": datetime.now().isoformat()}
        
    except Exception as e:
        print(f"Error refreshing crisis cache: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to refresh crisis cache: {str(e)}")

@router.get("/crisis-summary")
async def get_crisis_summary(
    db: Session = Depends(get_db),
    current_user = Depends(get_optional_user)
):
    """
    Get quick crisis summary for dashboard overview
    """
    try:
        cache_key = "crisis_summary_quick"
        redis_client = await get_redis_client()
        
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return json.loads(cached_data)
        
        # Quick summary using conflict_events view
        summary = db.execute(text("""
            SELECT 
                COUNT(*) as total_incidents,
                SUM(fatalities) as total_fatalities,
                SUM(displaced_persons) as total_displaced,
                COUNT(DISTINCT state) as states_affected,
                COUNT(DISTINCT actor1) as unique_actors,
                COUNT(DISTINCT event_type) as crisis_types
            FROM conflict_events
        """)).first()
        
        result = {
            "total_incidents": summary.total_incidents or 0,
            "total_fatalities": summary.total_fatalities or 0,
            "total_displaced": summary.total_displaced or 0,
            "states_affected": summary.states_affected or 0,
            "unique_actors": summary.unique_actors or 0,
            "crisis_types": summary.crisis_types or 0,
            "last_updated": datetime.now().isoformat()
        }
        
        # Cache for 5 minutes
        await redis_client.setex(cache_key, 300, json.dumps(result))
        
        return result
        
    except Exception as e:
        print(f"Error in crisis summary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch crisis summary: {str(e)}")
