from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, date, timedelta
from uuid import UUID

from app.db.database import get_db
from app.models.conflict import ConflictEvent
from app.models.auth import User
from app.api.deps import get_current_user, require_role, get_optional_user
from app.schemas.conflict import (
    ConflictEvent as ConflictEventSchema,
    ConflictEventCreate,
    ConflictEventUpdate,
    ConflictSummary,
    ConflictStats
)

router = APIRouter()


@router.get("/", response_model=List[ConflictEventSchema])
async def get_conflicts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=10000),
    state: Optional[str] = Query(None),
    lga: Optional[str] = Query(None),
    event_type: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """Get list of conflict events with optional filtering"""
    query = db.query(ConflictEvent)
    
    if state:
        query = query.filter(ConflictEvent.state == state)
    if lga:
        query = query.filter(ConflictEvent.lga == lga)
    if event_type:
        query = query.filter(ConflictEvent.event_type == event_type)
    if start_date:
        query = query.filter(ConflictEvent.event_date >= start_date)
    if end_date:
        query = query.filter(ConflictEvent.event_date <= end_date)
    
    # Order by date descending
    query = query.order_by(ConflictEvent.event_date.desc())
    
    conflicts = query.offset(skip).limit(limit).all()
    return conflicts


@router.get("/{conflict_id}", response_model=ConflictEventSchema)
async def get_conflict(conflict_id: UUID, db: Session = Depends(get_db)):
    """Get specific conflict event by ID"""
    conflict = db.query(ConflictEvent).filter(ConflictEvent.id == conflict_id).first()
    if not conflict:
        raise HTTPException(status_code=404, detail="Conflict event not found")
    return conflict


@router.post("/", response_model=ConflictEventSchema)
async def create_conflict(
    conflict: ConflictEventCreate,
    current_user: User = Depends(require_role("analyst")),
    db: Session = Depends(get_db)
):
    """Create new conflict record.
    
    **Requires:** Analyst or Admin role
    """
    db_conflict = ConflictEvent(**conflict.dict())
    db.add(db_conflict)
    db.commit()
    db.refresh(db_conflict)
    return db_conflict


@router.put("/{conflict_id}", response_model=ConflictEventSchema)
async def update_conflict(
    conflict_id: UUID, 
    conflict_update: ConflictEventUpdate,
    current_user: User = Depends(require_role("analyst")),
    db: Session = Depends(get_db)
):
    """Update conflict record.
    
    **Requires:** Analyst or Admin role
    """
    db_conflict = db.query(ConflictEvent).filter(ConflictEvent.id == conflict_id).first()
    if not db_conflict:
        raise HTTPException(status_code=404, detail="Conflict not found")
    
    update_data = conflict_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_conflict, field, value)
    
    db.commit()
    db.refresh(db_conflict)
    return db_conflict


@router.delete("/{conflict_id}")
async def delete_conflict(
    conflict_id: UUID,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Delete conflict record.
    
    **Requires:** Admin role only
    """
    db_conflict = db.query(ConflictEvent).filter(ConflictEvent.id == conflict_id).first()
    if not db_conflict:
        raise HTTPException(status_code=404, detail="Conflict not found")
    
    db.delete(db_conflict)
    db.commit()
    return {"message": "Conflict deleted successfully"}


@router.get("/summary/overview", response_model=ConflictSummary)
async def get_conflict_summary(db: Session = Depends(get_db)):
    """Get overall conflict summary statistics"""
    
    # Get totals
    total_incidents = db.query(ConflictEvent).count()
    
    # Sum casualties
    from sqlalchemy import func
    casualty_sums = db.query(
        func.sum(ConflictEvent.fatalities).label('fatalities'),
        func.sum(ConflictEvent.injuries).label('injured'),
        func.sum(ConflictEvent.displaced_persons).label('displaced')
    ).first()
    
    # Count unique states and LGAs
    states_affected = db.query(ConflictEvent.state).distinct().count()
    lgas_affected = db.query(ConflictEvent.lga).filter(ConflictEvent.lga.isnot(None)).distinct().count()
    
    return ConflictSummary(
        total_incidents=total_incidents,
        total_fatalities=casualty_sums.fatalities or 0,
        total_injured=casualty_sums.injured or 0,
        total_displaced=casualty_sums.displaced or 0,
        states_affected=states_affected,
        lgas_affected=lgas_affected
    )


@router.get("/summary/dashboard")
async def get_dashboard_summary(db: Session = Depends(get_db)):
    """Get dashboard summary statistics with period comparisons"""
    
    # Date ranges for current and previous periods (30 days)
    now = datetime.now().date()
    thirty_days_ago = now - timedelta(days=30)
    sixty_days_ago = now - timedelta(days=60)
    
    # Current period (last 30 days)
    current_period_incidents = db.query(ConflictEvent).filter(
        ConflictEvent.event_date >= thirty_days_ago
    ).count()
    
    current_period_fatalities = db.query(
        func.sum(ConflictEvent.fatalities)
    ).filter(
        ConflictEvent.event_date >= thirty_days_ago
    ).scalar() or 0
    
    # Previous period (30-60 days ago)
    previous_period_incidents = db.query(ConflictEvent).filter(
        ConflictEvent.event_date >= sixty_days_ago,
        ConflictEvent.event_date < thirty_days_ago
    ).count()
    
    previous_period_fatalities = db.query(
        func.sum(ConflictEvent.fatalities)
    ).filter(
        ConflictEvent.event_date >= sixty_days_ago,
        ConflictEvent.event_date < thirty_days_ago
    ).scalar() or 0
    
    # Calculate percentage changes
    incidents_change = 0
    if previous_period_incidents > 0:
        incidents_change = ((current_period_incidents - previous_period_incidents) / previous_period_incidents) * 100
    
    fatalities_change = 0
    if previous_period_fatalities > 0:
        fatalities_change = ((current_period_fatalities - previous_period_fatalities) / previous_period_fatalities) * 100
    
    # Active hotspots (LGAs with 5+ incidents in last 30 days)
    hotspot_count = db.query(
        ConflictEvent.state,
        ConflictEvent.lga
    ).filter(
        ConflictEvent.event_date >= thirty_days_ago
    ).group_by(
        ConflictEvent.state, ConflictEvent.lga
    ).having(
        func.count(ConflictEvent.id) >= 5
    ).count()
    
    # Previous period hotspots for comparison
    previous_hotspot_count = db.query(
        ConflictEvent.state,
        ConflictEvent.lga
    ).filter(
        ConflictEvent.event_date >= sixty_days_ago,
        ConflictEvent.event_date < thirty_days_ago
    ).group_by(
        ConflictEvent.state, ConflictEvent.lga
    ).having(
        func.count(ConflictEvent.id) >= 5
    ).count()
    
    hotspots_change = 0
    if previous_hotspot_count > 0:
        hotspots_change = ((hotspot_count - previous_hotspot_count) / previous_hotspot_count) * 100
    
    # States affected in last 30 days
    states_affected = db.query(ConflictEvent.state).filter(
        ConflictEvent.event_date >= thirty_days_ago
    ).distinct().count()
    
    # Total states in Nigeria
    total_states = 36
    
    # Last updated
    latest_event = db.query(ConflictEvent.event_date).order_by(
        ConflictEvent.event_date.desc()
    ).first()
    
    last_updated = latest_event[0].isoformat() if latest_event else now.isoformat()
    
    return {
        "totalIncidents": current_period_incidents,
        "totalIncidentsChange": round(incidents_change, 1),
        "fatalities": int(current_period_fatalities),
        "fatalitiesChange": round(fatalities_change, 1),
        "activeHotspots": hotspot_count,
        "activeHotspotsChange": round(hotspots_change, 1),
        "statesAffected": states_affected,
        "totalStates": total_states,
        "statesAffectedChange": 0,  # Can be calculated similarly if needed
        "lastUpdated": last_updated
    }


@router.get("/test/simple")
async def test_simple():
    """Simple test endpoint"""
    return {"status": "ok", "message": "API is working"}

@router.get("/test/db")
async def test_db(db: Session = Depends(get_db)):
    """Test database connection"""
    try:
        count = db.query(ConflictEvent).count()
        return {"status": "ok", "conflicts_count": count}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.get("/stats/dashboard", response_model=ConflictStats)
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics"""
    
    try:
        # Count total conflicts first
        total_conflicts = db.query(ConflictEvent).count()
        print(f"Total conflicts in DB: {total_conflicts}")
        
        # By state
        state_stats = db.query(
            ConflictEvent.state,
            func.count(ConflictEvent.id).label('incidents'),
            func.sum(ConflictEvent.fatalities).label('fatalities')
        ).group_by(ConflictEvent.state).order_by(func.count(ConflictEvent.id).desc()).all()
        
        # By conflict type
        conflict_type_stats = db.query(
            ConflictEvent.conflict_type,
            func.count(ConflictEvent.id).label('incidents')
        ).group_by(ConflictEvent.conflict_type).order_by(func.count(ConflictEvent.id).desc()).all()
        
        # By month (last 12 months)
        twelve_months_ago = datetime.now().date() - timedelta(days=365)
        monthly_stats = db.query(
            func.date_trunc('month', ConflictEvent.event_date).label('month'),
            func.count(ConflictEvent.id).label('incidents'),
            func.sum(ConflictEvent.fatalities).label('fatalities')
        ).filter(ConflictEvent.event_date >= twelve_months_ago).group_by('month').order_by('month').all()
        
        # Total casualty stats (gender-disaggregated data not available)
        casualty_stats = db.query(
            func.sum(ConflictEvent.fatalities).label('total_fatalities'),
            func.sum(ConflictEvent.kidnapped).label('total_kidnapped')
        ).first()
        
        return ConflictStats(
            by_state=[{"state": s.state, "incidents": s.incidents, "fatalities": s.fatalities or 0} for s in state_stats],
            by_event_type=[{"event_type": e.conflict_type, "incidents": e.incidents} for e in conflict_type_stats],
            by_month=[{"month": str(m.month), "incidents": m.incidents, "fatalities": m.fatalities or 0} for m in monthly_stats],
            gender_impact={
                "male_fatalities": 0,  # Gender-disaggregated data not available
                "female_fatalities": 0,
                "male_kidnapped": 0,
                "female_kidnapped": 0
            }
        )
    except Exception as e:
        print(f"Error in stats endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/heatmap/data")
async def get_heatmap_data(
    days_back: int = Query(30, ge=1),
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """
    Get heatmap data: list of [latitude, longitude, intensity] points
    Intensity is based on incident count and fatalities within spatial regions
    """
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        # Get all conflicts with coordinates in the last N days
        conflicts = db.query(
            ConflictEvent.latitude,
            ConflictEvent.longitude,
            ConflictEvent.fatalities,
            ConflictEvent.event_date
        ).filter(
            ConflictEvent.latitude.isnot(None),
            ConflictEvent.longitude.isnot(None),
            ConflictEvent.event_date >= cutoff_date
        ).all()
        
        if not conflicts:
            return {"points": [], "bounds": {"north": 13.8, "south": 2.7, "east": 14.68, "west": 2.67}}
        
        # Convert to heatmap format: [lat, lng, intensity]
        # Intensity = 1 + (fatalities / max_fatalities) * 9  (scale 1-10)
        max_fatalities = max([c.fatalities or 0 for c in conflicts]) or 1
        
        points = []
        for conflict in conflicts:
            lat = float(conflict.latitude)
            lng = float(conflict.longitude)
            # Intensity: 1-10 scale, higher fatalities = higher intensity
            fatalities = conflict.fatalities or 0
            intensity = 1 + (fatalities / max_fatalities) * 9
            points.append([lat, lng, intensity])
        
        # Get bounds for Nigeria
        return {
            "points": points,
            "bounds": {
                "north": 13.8,
                "south": 2.7,
                "east": 14.68,
                "west": 2.67
            }
        }
    except Exception as e:
        print(f"Error in heatmap endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))
