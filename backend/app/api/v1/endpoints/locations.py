from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.database import get_db
from app.models.location import Location

router = APIRouter()


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
    
    locations = query.order_by(Location.name).all()
    
    return [
        {
            "id": location.id,
            "name": location.name,
            "type": location.type,
            "parent_id": location.parent_id,
            "population": location.population,
            "poverty_rate": location.poverty_rate,
            "unemployment_rate": location.unemployment_rate
        }
        for location in locations
    ]


@router.get("/states")
async def get_states(db: Session = Depends(get_db)):
    """Get all Nigerian states"""
    states = db.query(Location).filter(Location.type == "state").order_by(Location.name).all()
    
    return [
        {
            "id": state.id,
            "name": state.name,
            "population": state.population,
            "poverty_rate": state.poverty_rate,
            "unemployment_rate": state.unemployment_rate
        }
        for state in states
    ]


@router.get("/states/{state_name}/lgas")
async def get_state_lgas(state_name: str, db: Session = Depends(get_db)):
    """Get all LGAs in a state"""
    state = db.query(Location).filter(Location.name == state_name, Location.type == "state").first()
    if not state:
        return {"error": "State not found"}
    
    lgas = db.query(Location).filter(Location.parent_id == state.id, Location.type == "lga").order_by(Location.name).all()
    
    return [
        {
            "id": lga.id,
            "name": lga.name,
            "population": lga.population,
            "poverty_rate": lga.poverty_rate,
            "unemployment_rate": lga.unemployment_rate
        }
        for lga in lgas
    ]


@router.get("/hierarchy")
async def get_location_hierarchy(db: Session = Depends(get_db)):
    """Get complete location hierarchy (states -> LGAs -> communities)"""
    states = db.query(Location).filter(Location.type == "state").order_by(Location.name).all()
    
    hierarchy = []
    for state in states:
        lgas = db.query(Location).filter(Location.parent_id == state.id, Location.type == "lga").order_by(Location.name).all()
        
        state_data = {
            "id": state.id,
            "name": state.name,
            "type": "state",
            "lgas": []
        }
        
        for lga in lgas:
            communities = db.query(Location).filter(Location.parent_id == lga.id, Location.type == "community").order_by(Location.name).all()
            
            lga_data = {
                "id": lga.id,
                "name": lga.name,
                "type": "lga",
                "communities": [
                    {
                        "id": community.id,
                        "name": community.name,
                        "type": "community"
                    }
                    for community in communities
                ]
            }
            
            state_data["lgas"].append(lga_data)
        
        hierarchy.append(state_data)
    
    return hierarchy
