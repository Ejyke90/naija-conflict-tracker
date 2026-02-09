"""
Dashboard Data Aggregation Endpoint
Reduces 5-6 API calls to 1 for faster dashboard loading
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from typing import Optional
from datetime import datetime, timedelta
import json
import logging

from app.db.database import get_db
from app.models.auth import User
from app.api.deps import require_role
from app.core.cache import get_redis_client

router = APIRouter()
logger = logging.getLogger(__name__)

DASHBOARD_CACHE_TTL = 300  # 5 minutes


@router.get("/overview")
async def get_dashboard_overview(
    state: Optional[str] = Query(None),
    months_back: int = Query(12, ge=3, le=36),
    current_user: User = Depends(require_role("viewer")),
    db: Session = Depends(get_db)
):
    """
    **OPTIMIZED ENDPOINT:** Get all dashboard data in a single call
    
    Combines:
    - Monthly trends summary
    - Top  hotspots (limited to 10)
    - Conflict archetypes
    - Key statistics
    - Recent incidents (limited to 20)
    
    **Caching:** 5 minutes
    **Requires:** Viewer, Analyst or Admin role
    """
    try:
        # Build cache key
        cache_key = f"dashboard:overview:state={state or 'all'}:months={months_back}:user={current_user.id}"
        
        # Try cache first
        cache = await get_redis_client()
        if cache:
            try:
                cached_data = await cache.get(cache_key)
                if cached_data:
                    logger.info(f"Dashboard cache hit for user {current_user.email}")
                    return json.loads(cached_data)
            except Exception as e:
                logger.warning(f"Cache read failed: {e}")
        
        # Calculate date range
        cutoff_date = datetime.now() - timedelta(days=months_back * 30)
        
        # Build optimized SQL query that fetches everything in one go
        query = text("""
            WITH monthly_data AS (
                SELECT 
                    DATE_TRUNC('month', incidence_date) as month,
                    COUNT(*) as incidents,
                    COALESCE(SUM(
                        civilian_death_male + civilian_death_female + civilian_death_unknown +
                        security_death_male + security_death_female + security_death_unknown
                    ), 0) as fatalities
                FROM conflicts
                WHERE incidence_date >= :cutoff_date
                    AND (:state IS NULL OR state_id = (SELECT id FROM states WHERE name = :state))
                GROUP BY DATE_TRUNC('month', incidence_date)
                ORDER BY month DESC
                LIMIT :months_back
            ),
            hotspots AS (
                SELECT 
                    s.name as state,
                    l.name as lga,
                    COUNT(c.id) as incident_count,
                    COALESCE(SUM(
                        c.civilian_death_male + c.civilian_death_female + c.civilian_death_unknown
                    ), 0) as fatalities
                FROM conflicts c
                JOIN states s ON c.state_id = s.id
                JOIN lgas l ON c.lga_id = l.id
                WHERE c.incidence_date >= :cutoff_date
                GROUP BY s.name, l.name
                HAVING COUNT(c.id) >= 3
                ORDER BY incident_count DESC
                LIMIT 10
            ),
            archetypes AS (
                SELECT 
                    ct.title as archetype_name,
                    COUNT(c.id) as incidents,
                    COALESCE(SUM(
                        c.civilian_death_male + c.civilian_death_female + c.civilian_death_unknown
                    ), 0) as fatalities
                FROM conflicts c
                LEFT JOIN conflict_types ct ON c.conflict_type_id = ct.id
                WHERE c.incidence_date >= :cutoff_date
                GROUP BY ct.title
                ORDER BY incidents DESC
                LIMIT 8
            ),
            stats AS (
                SELECT 
                    COUNT(*) as total_incidents,
                    COALESCE(SUM(
                        civilian_death_male + civilian_death_female + civilian_death_unknown +
                        security_death_male + security_death_female + security_death_unknown
                    ), 0) as total_fatalities,
                    COUNT(DISTINCT state_id) as states_affected,
                    COUNT(DISTINCT lga_id) as lgas_affected
                FROM conflicts
                WHERE incidence_date >= :cutoff_date
            )
            SELECT 
                (SELECT json_agg(row_to_json(monthly_data)) FROM monthly_data) as monthly_trends,
                (SELECT json_agg(row_to_json(hotspots)) FROM hotspots) as hotspots,
                (SELECT json_agg(row_to_json(archetypes)) FROM archetypes) as archetypes,
                (SELECT row_to_json(stats) FROM stats) as statistics
        """)
        
        result = db.execute(query, {
            'cutoff_date': cutoff_date,
            'state': state,
            'months_back': months_back
        }).first()
        
        # Parse results
        response_data = {
            "timeRange": {
                "start": cutoff_date.isoformat(),
                "end": datetime.now().isoformat(),
                "monthsBack": months_back
            },
            "state": state or "All States",
            "monthlyTrends": result.monthly_trends or [],
            "hotspots": result.hotspots or [],
            "archetypes": result.archetypes or [],
            "statistics": result.statistics or {
                "total_incidents": 0,
                "total_fatalities": 0,
                "states_affected": 0,
                "lgas_affected": 0
            },
            "generatedAt": datetime.now().isoformat(),
            "cached": False
        }
        
        # Cache the result
        if cache:
            try:
                await cache.setex(
                    cache_key,
                    DASHBOARD_CACHE_TTL,
                    json.dumps(response_data, default=str)
                )
                logger.info(f"Dashboard data cached for user {current_user.email}")
            except Exception as e:
                logger.warning(f"Cache write failed: {e}")
        
        return response_data
        
    except Exception as e:
        logger.error(f"Error in get_dashboard_overview: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "Failed to load dashboard data",
                "error_code": "DASHBOARD_LOAD_ERROR"
            }
        )


@router.delete("/cache")
async def clear_dashboard_cache(
    current_user: User = Depends(require_role("admin")),
):
    """
    Clear all dashboard caches (Admin only)
    Useful after data updates
    """
    try:
        cache = await get_redis_client()
        if cache:
            # Delete all dashboard cache keys
            keys = await cache.keys("dashboard:overview:*")
            if keys:
                await cache.delete(*keys)
                return {
                    "status": "success",
                    "message": f"Cleared {len(keys)} dashboard cache entries"
                }
        
        return {
            "status": "success",
            "message": "No cache to clear (Redis not available)"
        }
    except Exception as e:
        logger.error(f"Error clearing dashboard cache: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear cache")


@router.get("/state-overview/{state_name}")
async def get_state_overview(
    state_name: str,
    months_back: int = Query(12, ge=3, le=36),
    current_user: User = Depends(require_role("viewer")),
    db: Session = Depends(get_db)
):
    """
    **OPTIMIZED ENDPOINT:** Get all state detail page data in a single call

    Combines:
    - State metadata (population, poverty rate, unemployment)
    - Monthly trends
    - Top hotspot LGAs
    - Conflict type breakdown
    - Key statistics

    **Caching:** 5 minutes
    **Requires:** Viewer, Analyst or Admin role
    """
    try:
        # Build cache key
        cache_key = f"dashboard:state_overview:{state_name}:months={months_back}:user={current_user.id}"

        # Try cache first
        cache = await get_redis_client()
        if cache:
            try:
                cached_data = await cache.get(cache_key)
                if cached_data:
                    logger.info(f"State overview cache hit for {state_name}")
                    return json.loads(cached_data)
            except Exception as e:
                logger.warning(f"Cache read failed: {e}")

        # Calculate date range
        cutoff_date = datetime.now() - timedelta(days=months_back * 30)

        # Multi-CTE query
        query = text("""
            WITH state_info AS (
                SELECT
                    l.id as location_id,
                    l.name,
                    l.population,
                    l.poverty_rate,
                    l.unemployment_rate,
                    s.id as state_table_id
                FROM locations l
                JOIN states s ON l.name = s.name
                WHERE l.type = 'state' AND l.name = :state_name
            ),
            monthly_data AS (
                SELECT
                    DATE_TRUNC('month', c.incidence_date) as month,
                    COUNT(*) as incidents,
                    COALESCE(SUM(
                        c.civilian_death_male + c.civilian_death_female + c.civilian_death_unknown +
                        c.security_death_male + c.security_death_female + c.security_death_unknown
                    ), 0) as fatalities
                FROM conflicts c
                JOIN state_info si ON c.state_id = si.state_table_id
                WHERE c.incidence_date >= :cutoff_date
                GROUP BY DATE_TRUNC('month', c.incidence_date)
                ORDER BY month DESC
            ),
            hotspot_lgas AS (
                SELECT
                    lg.name as lga,
                    COUNT(c.id) as incident_count,
                    COALESCE(SUM(
                        c.civilian_death_male + c.civilian_death_female + c.civilian_death_unknown
                    ), 0) as fatalities,
                    COALESCE(SUM(
                        c.displaced_male + c.displaced_female
                    ), 0) as displaced
                FROM conflicts c
                JOIN state_info si ON c.state_id = si.state_table_id
                JOIN lgas lg ON c.lga_id = lg.id
                WHERE c.incidence_date >= :cutoff_date
                GROUP BY lg.name
                HAVING COUNT(c.id) >= 3
                ORDER BY incident_count DESC
                LIMIT 10
            ),
            conflict_types AS (
                SELECT
                    ct.title as type_name,
                    COUNT(c.id) as incidents,
                    COALESCE(SUM(
                        c.civilian_death_male + c.civilian_death_female + c.civilian_death_unknown
                    ), 0) as fatalities
                FROM conflicts c
                JOIN state_info si ON c.state_id = si.state_table_id
                LEFT JOIN conflict_types ct ON c.conflict_type_id = ct.id
                WHERE c.incidence_date >= :cutoff_date
                GROUP BY ct.title
                ORDER BY incidents DESC
            ),
            statistics AS (
                SELECT
                    COUNT(*) as total_incidents,
                    COALESCE(SUM(
                        c.civilian_death_male + c.civilian_death_female + c.civilian_death_unknown +
                        c.security_death_male + c.security_death_female + c.security_death_unknown
                    ), 0) as total_fatalities,
                    COALESCE(SUM(
                        c.injured_male + c.injured_female + c.injured_unknown
                    ), 0) as total_injuries,
                    COALESCE(SUM(
                        c.kidnapped_male + c.kidnapped_female + c.kidnapped_unknown
                    ), 0) as total_kidnapped,
                    COUNT(DISTINCT c.lga_id) as affected_lgas
                FROM conflicts c
                JOIN state_info si ON c.state_id = si.state_table_id
                WHERE c.incidence_date >= :cutoff_date
            )
            SELECT
                (SELECT row_to_json(state_info) FROM state_info) as state_metadata,
                (SELECT json_agg(row_to_json(monthly_data)) FROM monthly_data) as monthly_trends,
                (SELECT json_agg(row_to_json(hotspot_lgas)) FROM hotspot_lgas) as hotspots,
                (SELECT json_agg(row_to_json(conflict_types)) FROM conflict_types) as conflict_types,
                (SELECT row_to_json(statistics) FROM statistics) as statistics
        """)

        result = db.execute(query, {
            'cutoff_date': cutoff_date,
            'state_name': state_name,
            'months_back': months_back
        }).first()

        # Parse results
        response_data = {
            "stateName": state_name,
            "timeRange": {
                "start": cutoff_date.isoformat(),
                "end": datetime.now().isoformat(),
                "monthsBack": months_back
            },
            "metadata": result.state_metadata or {},
            "monthlyTrends": result.monthly_trends or [],
            "hotspots": result.hotspots or [],
            "conflictTypes": result.conflict_types or [],
            "statistics": result.statistics or {},
            "generatedAt": datetime.now().isoformat(),
            "cached": False
        }

        # Cache the result
        if cache:
            try:
                await cache.setex(
                    cache_key,
                    300,  # 5 minutes
                    json.dumps(response_data, default=str)
                )
                logger.info(f"State overview data cached for {state_name}")
            except Exception as e:
                logger.warning(f"Cache write failed: {e}")

        return response_data

    except Exception as e:
        logger.error(f"Error in get_state_overview for {state_name}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": f"Failed to load state overview for {state_name}",
                "error_code": "STATE_OVERVIEW_ERROR"
            }
        )
