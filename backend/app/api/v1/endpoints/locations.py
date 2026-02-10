from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from typing import List, Optional
import logging
import json

from app.db.database import get_db
from app.models.location import Location
from app.models.reference import State
from app.models.conflict import Conflict
from app.core.cache import get_redis_client

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/")
async def get_locations(
    location_type: Optional[str] = Query(None, pattern="^(state|lga|community)$"),
    parent_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Get locations with optional filtering"""
    query = db.query(Location)
    
    if location_type:
        query = query.filter(Location.type == location_type)
    if parent_id:
        query = query.filter(Location.parent_id == parent_id)
    
    locations = query.order_by(Location.title).all()
    
    return [
        {
            "id": location.id,
            "name": location.title,
            "type": location.type,
            "parent_id": location.parent_id,
            "population": location.population,
            "poverty_rate": location.poverty_rate,
            "unemployment_rate": location.unemployment_rate
        }
        for location in locations
    ]


@router.get("/health")
async def check_locations_health(db: Session = Depends(get_db)):
    """Verify locations table is properly seeded with states and LGAs"""
    try:
        state_count = db.query(Location).filter(Location.type == "state").count()
        lga_count = db.query(Location).filter(Location.type == "lga").count()

        sample_states = db.query(Location.title).filter(
            Location.type == "state"
        ).order_by(Location.title).limit(5).all()

        return {
            "status": "healthy" if state_count >= 37 else "unhealthy",
            "state_count": state_count,
            "lga_count": lga_count,
            "expected_states": 37,
            "sample_states": [s[0] for s in sample_states],
            "message": f"Locations table contains {state_count} states and {lga_count} LGAs"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "state_count": 0,
            "lga_count": 0
        }


@router.get("/states")
async def get_states(db: Session = Depends(get_db)):
    """Get all Nigerian states (PUBLIC - cached 24h)"""
    try:
        # Try cache first
        cache = await get_redis_client()
        cache_key = "locations:states"

        if cache:
            try:
                cached = await cache.get(cache_key)
                if cached:
                    logger.info("Cache hit for states lookup")
                    return json.loads(cached)
            except Exception as e:
                logger.warning(f"Cache read failed: {e}")

        # Simple query - just get states from the states reference table
        query = text("""
            SELECT
                id,
                title,
                created_at
            FROM states
            ORDER BY title ASC
        """)

        result = db.execute(query).fetchall()

        if not result:
            # Fallback: try locations table
            logger.warning("No states found in states table, trying locations table")
            query = text("""
                SELECT
                    id,
                    title
                FROM locations
                WHERE type = 'state'
                ORDER BY title ASC
            """)
            result = db.execute(query).fetchall()

        response = [
            {
                "id": row.id,
                "name": row.title
            }
            for row in result
        ]

        # Cache for 24 hours
        if cache:
            try:
                await cache.setex(cache_key, 86400, json.dumps(response))
                logger.info("Cached states data for 24 hours")
            except Exception as e:
                logger.warning(f"Cache write failed: {e}")

        return response

    except Exception as e:
        logger.error(f"Error in get_states: {str(e)}", exc_info=True)
        # Return hardcoded states as ultimate fallback
        return [
            {"id": i, "name": state}
            for i, state in enumerate([
                "Abia", "Adamawa", "Akwa Ibom", "Anambra", "Bauchi", "Bayelsa",
                "Benue", "Borno", "Cross River", "Delta", "Ebonyi", "Edo",
                "Ekiti", "Enugu", "Gombe", "Imo", "Jigawa", "Kaduna", "Kano",
                "Katsina", "Kebbi", "Kogi", "Kwara", "Lagos", "Nasarawa", "Niger",
                "Ogun", "Ondo", "Osun", "Oyo", "Plateau", "Rivers", "Sokoto",
                "Taraba", "Yobe", "Zamfara", "FCT"
            ], start=1)
        ]


@router.get("/states/{state_name}/lgas")
async def get_state_lgas(state_name: str, db: Session = Depends(get_db)):
    """Get all LGAs in a state"""
    state = db.query(Location).filter(Location.title == state_name, Location.type == "state").first()
    if not state:
        return {"error": "State not found"}
    
    lgas = db.query(Location).filter(Location.parent_id == state.id, Location.type == "lga").order_by(Location.title).all()
    
    return [
        {
            "id": lga.id,
            "name": lga.title,
            "population": lga.population,
            "poverty_rate": lga.poverty_rate,
            "unemployment_rate": lga.unemployment_rate
        }
        for lga in lgas
    ]


@router.get("/hierarchy")
async def get_location_hierarchy(db: Session = Depends(get_db)):
    """Get complete location hierarchy (states -> LGAs -> communities)"""
    states = db.query(Location).filter(Location.type == "state").order_by(Location.title).all()
    
    hierarchy = []
    for state in states:
        lgas = db.query(Location).filter(Location.parent_id == state.id, Location.type == "lga").order_by(Location.title).all()
        
        state_data = {
            "id": state.id,
            "name": state.title,
            "type": "state",
            "lgas": []
        }
        
        for lga in lgas:
            communities = db.query(Location).filter(Location.parent_id == lga.id, Location.type == "community").order_by(Location.title).all()
            
            lga_data = {
                "id": lga.id,
                "name": lga.title,
                "type": "lga",
                "communities": [
                    {
                        "id": community.id,
                        "name": community.title,
                        "type": "community"
                    }
                    for community in communities
                ]
            }
            
            state_data["lgas"].append(lga_data)
        
        hierarchy.append(state_data)
    
    return hierarchy
