"""
Simple data import endpoint for Railway deployment
"""

from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from uuid import uuid4
from geoalchemy2 import WKTElement

from app.db.database import get_db
from app.models.conflict import Conflict

router = APIRouter(prefix="/api/simple-import", tags=["simple-import"])

@router.post("/sample-data")
async def import_sample_data(db: Session = Depends(get_db)):
    """Import sample conflict data for testing"""
    
    try:
        # Sample conflict data
        sample_conflicts = [
            {
                "event_date": datetime(2021, 6, 2),
                "state": "Katsina",
                "lga": "Jibia",
                "community": "Zandam",
                "perpetrator_group": "Bandits",
                "event_type": "armed_attack",
                "archetype": "banditry",
                "description": "Bandit attack in Zandam community",
                "latitude": 12.9317,
                "longitude": 8.0967
            },
            {
                "event_date": datetime(2021, 6, 15),
                "state": "Imo",
                "lga": "Oru East",
                "community": "Awonmama",
                "perpetrator_group": "Assassins",
                "event_type": "conflict",
                "archetype": "unknown",
                "description": "Attack by unknown assailants in Awonmama",
                "latitude": 5.5339,
                "longitude": 7.0488
            },
            {
                "event_date": datetime(2021, 6, 30),
                "state": "Katsina",
                "lga": "Funtua",
                "community": "Zamfara - Kano Highway",
                "perpetrator_group": "Bandits",
                "event_type": "armed_attack",
                "archetype": "banditry",
                "description": "Banditry incident on highway",
                "latitude": 11.5339,
                "longitude": 7.5488
            }
        ]
        
        imported_count = 0
        for data in sample_conflicts:
            conflict = Conflict(
                id=str(uuid4()),
                event_date=data["event_date"],
                event_type=data["event_type"],
                archetype=data["archetype"],
                description=data["description"],
                state=data["state"],
                lga=data["lga"],
                community=data["community"],
                location_detail=f"{data['community']}, {data['lga']}, {data['state']}",
                coordinates=WKTElement(f'POINT({data["longitude"]} {data["latitude"]})', srid=4326),
                perpetrator_group=data["perpetrator_group"],
                source_type="sample_data",
                source_url="manual_import",
                source_reliability=4,
                confidence_score=0.8,
                verified=False,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            db.add(conflict)
            imported_count += 1
        
        db.commit()
        
        return {
            "status": "success",
            "message": f"Successfully imported {imported_count} sample records",
            "imported_count": imported_count
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")

@router.get("/count")
async def get_conflict_count(db: Session = Depends(get_db)):
    """Get current conflict count"""
    try:
        count = db.query(Conflict).count()
        return {"count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
