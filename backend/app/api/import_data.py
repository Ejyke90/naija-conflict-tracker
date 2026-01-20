"""
Data import endpoint for Railway deployment
"""

import pandas as pd
from fastapi import APIRouter, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from datetime import datetime
from uuid import uuid4
from geoalchemy2 import WKTElement
from typing import Dict, Any

from app.db.database import get_db
from app.models.conflict import Conflict

router = APIRouter(prefix="/api/import", tags=["import"])

def categorize_incident(perpetrator_group: str) -> tuple:
    """Categorize incident type and archetype based on perpetrator"""
    
    if not perpetrator_group:
        return 'conflict', 'unknown'
    
    perpetrator_lower = perpetrator_group.lower()
    
    # Determine event type and archetype
    if 'boko haram' in perpetrator_lower or 'iswap' in perpetrator_lower:
        return 'terrorism', 'terrorism'
    elif 'bandit' in perpetrator_lower:
        return 'armed_attack', 'banditry'
    elif 'herdsmen' in perpetrator_lower or 'farmer' in perpetrator_lower:
        return 'communal_violence', 'farmer_herder_conflict'
    elif 'security' in perpetrator_lower or 'police' in perpetrator_lower or 'military' in perpetrator_lower:
        return 'state_violence', 'extra_judicial_killings'
    elif 'cultist' in perpetrator_lower:
        return 'gang_violence', 'cultism'
    elif 'gunmen' in perpetrator_lower:
        return 'armed_attack', 'banditry'
    else:
        return 'conflict', 'unknown'

def geocode_location(state: str, lga: str, community: str) -> tuple:
    """Mock geocoding function"""
    
    state_coordinates = {
        'lagos': (6.5244, 3.3792),
        'abuja': (9.0765, 7.3986),
        'kano': (11.9804, 8.5168),
        'borno': (11.8313, 13.1059),
        'rivers': (4.8156, 7.0498),
        'delta': (5.5881, 5.7579),
        'enugu': (6.4419, 7.5018),
        'anambra': (6.2104, 6.9775),
        'imo': (5.5339, 7.0488),
        'abia': (5.4527, 7.5229),
    }
    
    if state and state.lower() in state_coordinates:
        return state_coordinates[state.lower()]
    
    # Default to Nigeria center if state not found
    return (9.0820, 8.6753)

@router.post("/excel")
async def import_excel_data(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Import Excel data directly to database"""
    
    try:
        # Read Excel file
        contents = await file.read()
        df = pd.read_excel(pd.ExcelFile(contents), sheet_name='Sheet2', header=None)
        
        # Parse data
        data_rows = []
        for idx, row in df.iterrows():
            if idx >= 4:  # Skip first 4 rows (headers)
                if pd.notna(row.iloc[0]) and isinstance(row.iloc[0], datetime):
                    incident = {
                        'event_date': row.iloc[0],
                        'community': row.iloc[1] if pd.notna(row.iloc[1]) else None,
                        'lga': row.iloc[2] if pd.notna(row.iloc[2]) else None,
                        'state': row.iloc[3] if pd.notna(row.iloc[3]) else None,
                        'region': row.iloc[4] if pd.notna(row.iloc[4]) else None,
                        'perpetrator_group': row.iloc[5] if pd.notna(row.iloc[5]) else None,
                        'event_type': 'conflict',
                        'archetype': 'unknown',
                        'description': f"Incident in {row.iloc[1] if pd.notna(row.iloc[1]) else 'Unknown location'}",
                        'source_type': 'excel_import',
                        'source_url': file.filename,
                        'source_reliability': 4,
                        'confidence_score': 0.8,
                        'verified': False
                    }
                    data_rows.append(incident)
        
        # Import to database
        imported_count = 0
        for row in data_rows:
            try:
                # Categorize the incident
                event_type, archetype = categorize_incident(row['perpetrator_group'])
                
                # Get coordinates
                latitude, longitude = geocode_location(row['state'], row['lga'], row['community'])
                
                # Create conflict record
                conflict = Conflict(
                    id=str(uuid4()),
                    event_date=row['event_date'],
                    event_type=event_type,
                    archetype=archetype,
                    description=row['description'],
                    state=row['state'] or 'Unknown',
                    lga=row['lga'],
                    community=row['community'],
                    location_detail=f"{row['community']}, {row['lga']}, {row['state']}",
                    coordinates=WKTElement(f'POINT({longitude} {latitude})', srid=4326),
                    perpetrator_group=row['perpetrator_group'],
                    source_type=row['source_type'],
                    source_url=row['source_url'],
                    source_reliability=row['source_reliability'],
                    confidence_score=row['confidence_score'],
                    verified=row['verified'],
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                
                db.add(conflict)
                imported_count += 1
                
            except Exception as e:
                print(f"Skipping record due to error: {e}")
                continue
        
        # Commit all changes
        db.commit()
        
        return {
            "status": "success",
            "message": f"Successfully imported {imported_count} records",
            "total_processed": len(data_rows),
            "imported_count": imported_count
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")
