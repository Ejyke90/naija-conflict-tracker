from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, timedelta

from app.db.database import get_db
from app.models.conflict import Conflict as ConflictModel
from app.schemas.conflict import Conflict, ConflictCreate, ConflictUpdate, ConflictSummary, ConflictStats

router = APIRouter()


@router.get("/", response_model=List[Conflict])
async def get_conflicts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    state: Optional[str] = Query(None),
    lga: Optional[str] = Query(None),
    event_type: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db)
):
    """Get list of conflicts with optional filtering"""
    query = db.query(ConflictModel)
    
    if state:
        query = query.filter(ConflictModel.state == state)
    if lga:
        query = query.filter(ConflictModel.lga == lga)
    if event_type:
        query = query.filter(ConflictModel.event_type == event_type)
    if start_date:
        query = query.filter(ConflictModel.event_date >= start_date)
    if end_date:
        query = query.filter(ConflictModel.event_date <= end_date)
    
    conflicts = query.offset(skip).limit(limit).all()
    return conflicts


@router.get("/{conflict_id}", response_model=Conflict)
async def get_conflict(conflict_id: str, db: Session = Depends(get_db)):
    """Get specific conflict by ID"""
    conflict = db.query(ConflictModel).filter(ConflictModel.id == conflict_id).first()
    if not conflict:
        raise HTTPException(status_code=404, detail="Conflict not found")
    return conflict


@router.post("/", response_model=Conflict)
async def create_conflict(conflict: ConflictCreate, db: Session = Depends(get_db)):
    """Create new conflict record"""
    db_conflict = ConflictModel(**conflict.dict())
    db.add(db_conflict)
    db.commit()
    db.refresh(db_conflict)
    return db_conflict


@router.put("/{conflict_id}", response_model=Conflict)
async def update_conflict(
    conflict_id: str, 
    conflict_update: ConflictUpdate, 
    db: Session = Depends(get_db)
):
    """Update conflict record"""
    db_conflict = db.query(ConflictModel).filter(ConflictModel.id == conflict_id).first()
    if not db_conflict:
        raise HTTPException(status_code=404, detail="Conflict not found")
    
    update_data = conflict_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_conflict, field, value)
    
    db.commit()
    db.refresh(db_conflict)
    return db_conflict


@router.delete("/{conflict_id}")
async def delete_conflict(conflict_id: str, db: Session = Depends(get_db)):
    """Delete conflict record"""
    db_conflict = db.query(ConflictModel).filter(ConflictModel.id == conflict_id).first()
    if not db_conflict:
        raise HTTPException(status_code=404, detail="Conflict not found")
    
    db.delete(db_conflict)
    db.commit()
    return {"message": "Conflict deleted successfully"}


@router.get("/summary/overview", response_model=ConflictSummary)
async def get_conflict_summary(db: Session = Depends(get_db)):
    """Get overall conflict summary statistics"""
    
    # Get totals
    total_incidents = db.query(ConflictModel).count()
    
    # Sum casualties
    from sqlalchemy import func
    casualty_sums = db.query(
        func.sum(ConflictModel.fatalities_male + ConflictModel.fatalities_female + ConflictModel.fatalities_unknown).label('fatalities'),
        func.sum(ConflictModel.injured_male + ConflictModel.injured_female + ConflictModel.injured_unknown).label('injured'),
        func.sum(ConflictModel.kidnapped_male + ConflictModel.kidnapped_female + ConflictModel.kidnapped_unknown).label('kidnapped'),
        func.sum(ConflictModel.displaced).label('displaced')
    ).first()
    
    # Count unique states and LGAs
    states_affected = db.query(ConflictModel.state).distinct().count()
    lgas_affected = db.query(ConflictModel.lga).filter(ConflictModel.lga.isnot(None)).distinct().count()
    
    return ConflictSummary(
        total_incidents=total_incidents,
        total_fatalities=casualty_sums.fatalities or 0,
        total_injured=casualty_sums.injured or 0,
        total_kidnapped=casualty_sums.kidnapped or 0,
        total_displaced=casualty_sums.displaced or 0,
        states_affected=states_affected,
        lgas_affected=lgas_affected
    )


@router.get("/stats/dashboard", response_model=ConflictStats)
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics"""
    
    # By state
    state_stats = db.query(
        ConflictModel.state,
        func.count(ConflictModel.id).label('incidents'),
        func.sum(ConflictModel.fatalities_male + ConflictModel.fatalities_female + ConflictModel.fatalities_unknown).label('fatalities')
    ).group_by(ConflictModel.state).order_by(func.count(ConflictModel.id).desc()).all()
    
    # By event type
    event_type_stats = db.query(
        ConflictModel.event_type,
        func.count(ConflictModel.id).label('incidents')
    ).group_by(ConflictModel.event_type).order_by(func.count(ConflictModel.id).desc()).all()
    
    # By month (last 12 months)
    twelve_months_ago = datetime.now() - timedelta(days=365)
    monthly_stats = db.query(
        func.date_trunc('month', ConflictModel.event_date).label('month'),
        func.count(ConflictModel.id).label('incidents'),
        func.sum(ConflictModel.fatalities_male + ConflictModel.fatalities_female + ConflictModel.fatalities_unknown).label('fatalities')
    ).filter(ConflictModel.event_date >= twelve_months_ago).group_by('month').order_by('month').all()
    
    # Gender impact
    gender_stats = db.query(
        func.sum(ConflictModel.fatalities_male).label('male_fatalities'),
        func.sum(ConflictModel.fatalities_female).label('female_fatalities'),
        func.sum(ConflictModel.kidnapped_male).label('male_kidnapped'),
        func.sum(ConflictModel.kidnapped_female).label('female_kidnapped')
    ).first()
    
    return ConflictStats(
        by_state=[{"state": s.state, "incidents": s.incidents, "fatalities": s.fatalities or 0} for s in state_stats],
        by_event_type=[{"event_type": e.event_type, "incidents": e.incidents} for e in event_type_stats],
        by_month=[{"month": str(m.month), "incidents": m.incidents, "fatalities": m.fatalities or 0} for m in monthly_stats],
        gender_impact={
            "male_fatalities": gender_stats.male_fatalities or 0,
            "female_fatalities": gender_stats.female_fatalities or 0,
            "male_kidnapped": gender_stats.male_kidnapped or 0,
            "female_kidnapped": gender_stats.female_kidnapped or 0
        }
    )
