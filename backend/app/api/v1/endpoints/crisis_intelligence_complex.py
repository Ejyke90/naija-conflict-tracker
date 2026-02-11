"""
Multi-Dimensional Crisis Intelligence Dashboard API
Optimized for Neon PostgreSQL with materialized views and Redis caching
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
    crisis_types_count: int

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
    Get comprehensive crisis intelligence data with optimized performance.
    
    Uses materialized views for fast queries and Redis caching for 15-minute TTL.
    """
    try:
        # Try to get from cache first
        cache_key = f"crisis_intelligence_{months_back}_{top_states}_{top_actors}"
        redis_client = await get_redis_client()
        
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return json.loads(cached_data)
        
        # Generate cutoff date
        cutoff_date = datetime.now().date() - timedelta(days=months_back * 30)
        
        # 1. Current Period Crisis Metrics (using conflict_events view)
        current_metrics = db.execute(text("""
            SELECT 
                SUM(incidents) as incidents,
                SUM(total_fatalities) as fatalities,
                SUM(total_displaced) as displaced,
                SUM(total_injuries) as injuries,
                SUM(crisis_index_score) as crisis_index_score,
                CASE 
                    WHEN SUM(crisis_index_score) >= 1000 THEN 'CRITICAL'
                    WHEN SUM(crisis_index_score) >= 500 THEN 'HIGH'
                    WHEN SUM(crisis_index_score) >= 200 THEN 'MEDIUM'
                    ELSE 'LOW'
                END as risk_level
            FROM (
                SELECT 
                    COUNT(*) as incidents,
                    SUM(fatalities) as total_fatalities,
                    SUM(displaced_persons) as total_displaced,
                    SUM(injuries) as total_injuries,
                    (SUM(fatalities) * 3 + SUM(displaced_persons) * 1 + SUM(injuries) * 0.5) as crisis_index_score
                FROM conflict_events 
                WHERE event_date >= :cutoff_date
            ) as metrics
        """), {"cutoff_date": cutoff_date}).first()
        
        # 2. State Hotspots (Top N by crisis index)
        state_hotspots_query = db.execute(text("""
            SELECT DISTINCT ON (state) 
                state,
                total_incidents,
                total_fatalities,
                total_displaced,
                crisis_index_score,
                risk_level,
                recent_incidents,
                recent_fatalities,
                crisis_types_count
            FROM crisis_state_hotspots 
            ORDER BY state, crisis_index_score DESC
            LIMIT :limit
        """), {"limit": top_states}).fetchall()
        
        # 3. Actor Threat Analysis (Top N by threat score)
        actor_threats_query = db.execute(text("""
            SELECT 
                actor,
                COALESCE(actor_type, 'Unknown') as actor_type,
                event_type,
                incidents,
                total_fatalities,
                total_displaced,
                threat_score,
                threat_level,
                states_affected
            FROM crisis_actor_analysis 
            ORDER BY threat_score DESC
            LIMIT :limit
        """), {"limit": top_actors}).fetchall()
        
        # 4. Crisis Type Distribution
        crisis_types_query = db.execute(text("""
            SELECT 
                event_type,
                conflict_type,
                total_incidents,
                total_fatalities,
                total_displaced,
                states_affected,
                trend_direction,
                recent_incidents
            FROM crisis_type_distribution 
            ORDER BY total_incidents DESC
        """)).fetchall()
        
        # 5. Monthly Trends
        monthly_trends_query = db.execute(text("""
            SELECT 
                month,
                SUM(incidents) as incidents,
                SUM(total_fatalities) as fatalities,
                SUM(total_displaced) as displaced,
                SUM(crisis_index_score) as crisis_score
            FROM crisis_monthly_summary 
            WHERE month >= to_char(:cutoff_date, 'YYYY-MM')
            GROUP BY month 
            ORDER BY month
        """), {"cutoff_date": cutoff_date}).fetchall()
        
        # Build response
        response = CrisisIntelligenceResponse(
            current_period=CrisisMetrics(
                incidents=current_metrics.incidents or 0,
                fatalities=current_metrics.fatalities or 0,
                displaced=current_metrics.displaced or 0,
                injuries=current_metrics.injuries or 0,
                crisis_index_score=float(current_metrics.crisis_index_score or 0),
                risk_level=current_metrics.risk_level or 'LOW'
            ),
            state_hotspots=[
                StateHotspot(
                    state=row.state,
                    total_incidents=row.total_incidents,
                    total_fatalities=row.total_fatalities,
                    total_displaced=row.total_displaced,
                    crisis_index_score=float(row.crisis_index_score),
                    risk_level=row.risk_level,
                    recent_incidents=row.recent_incidents,
                    recent_fatalities=row.recent_fatalities,
                    crisis_types_count=row.crisis_types_count
                ) for row in state_hotspots_query
            ],
            actor_threats=[
                ActorThreat(
                    actor=row.actor,
                    actor_type=row.actor_type,
                    event_type=row.event_type,
                    incidents=row.incidents,
                    total_fatalities=row.total_fatalities,
                    total_displaced=row.total_displaced,
                    threat_score=float(row.threat_score),
                    threat_level=row.threat_level,
                    states_affected=row.states_affected
                ) for row in actor_threats_query
            ],
            crisis_types=[
                CrisisType(
                    event_type=row.event_type,
                    conflict_type=row.conflict_type,
                    total_incidents=row.total_incidents,
                    total_fatalities=row.total_fatalities,
                    total_displaced=row.total_displaced,
                    states_affected=row.states_affected,
                    trend_direction=row.trend_direction,
                    recent_incidents=row.recent_incidents
                ) for row in crisis_types_query
            ],
            monthly_trends=[
                {
                    "month": row.month,
                    "incidents": row.incidents,
                    "fatalities": row.fatalities,
                    "displaced": row.displaced,
                    "crisis_score": float(row.crisis_score)
                } for row in monthly_trends_query
            ],
            last_updated=datetime.now().isoformat()
        )
        
        # Cache the response for 15 minutes (900 seconds)
        await redis_client.setex(cache_key, 900, response.json())
        
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
    Refresh materialized views for latest data.
    This should be called periodically or when data is updated.
    """
    try:
        # Refresh all materialized views
        db.execute(text("SELECT refresh_crisis_intelligence_views()"))
        db.commit()
        
        # Clear cache to force refresh
        redis_client = await get_redis_client()
        # Clear all crisis intelligence cache keys
        cache_keys = await redis_client.keys("crisis_intelligence_*")
        if cache_keys:
            await redis_client.delete(*cache_keys)
        
        return {"message": "Crisis intelligence views refreshed successfully", "timestamp": datetime.now().isoformat()}
        
    except Exception as e:
        print(f"Error refreshing crisis views: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to refresh crisis views: {str(e)}")

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
        
        # Quick summary using materialized views
        summary = db.execute(text("""
            SELECT 
                (SELECT SUM(total_incidents) FROM crisis_state_hotspots) as total_incidents,
                (SELECT SUM(total_fatalities) FROM crisis_state_hotspots) as total_fatalities,
                (SELECT SUM(total_displaced) FROM crisis_state_hotspots) as total_displaced,
                (SELECT COUNT(*) FROM crisis_state_hotspots WHERE risk_level = 'CRITICAL') as critical_states,
                (SELECT COUNT(*) FROM crisis_state_hotspots WHERE risk_level = 'HIGH') as high_risk_states,
                (SELECT COUNT(DISTINCT actor) FROM crisis_actor_analysis) as unique_actors,
                (SELECT COUNT(*) FROM crisis_type_distribution) as crisis_types
        """)).first()
        
        result = {
            "total_incidents": summary.total_incidents or 0,
            "total_fatalities": summary.total_fatalities or 0,
            "total_displaced": summary.total_displaced or 0,
            "critical_states": summary.critical_states or 0,
            "high_risk_states": summary.high_risk_states or 0,
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
