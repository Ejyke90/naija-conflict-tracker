"""
Conflicts API endpoints for the new normalized schema.
Uses the new Conflict model with foreign keys to actors, conflict_types, states, lgas.
"""
from typing import List, Optional
from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, and_, or_
from sqlalchemy.orm import Session, joinedload

from app.api import deps
from app.models.conflict import Conflict
from app.models.actor import Actor
from app.models.reference import ConflictType, State, LGA, Region
from app.schemas import conflict_new as schemas

router = APIRouter()


@router.get("/", response_model=List[schemas.ConflictWithDetails])
def list_conflicts(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    
    # Date filters
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    
    # Location filters (FK-based)
    region_id: Optional[int] = None,
    state_id: Optional[int] = None,
    lga_id: Optional[int] = None,
    community: Optional[str] = None,
    
    # Conflict type filter
    conflict_type_id: Optional[int] = None,
    
    # Actor filters
    actor_id: Optional[int] = Query(None, description="Filter by any actor (1, 2, or 3)"),
    
    # Verification filter
    verification_level: Optional[str] = None,
    
    # Sorting
    sort_by: str = Query("incidence_date", regex="^(incidence_date|total_deaths|id)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
):
    """
    List conflicts with filters and pagination.
    
    NEW FEATURES (vs legacy endpoint):
    - FK-based filtering (region_id, state_id, lga_id, conflict_type_id)
    - Actor filtering across all 3 actor columns
    - Gender-disaggregated casualty data
    - Joined reference data (actor names, conflict type names, location names)
    - Computed totals (total_deaths, total_injured, etc.)
    """
    # Base query with eager loading for JOINs
    query = db.query(Conflict).options(
        joinedload(Conflict.conflict_type_rel),
        joinedload(Conflict.region_rel),
        joinedload(Conflict.state_rel),
        joinedload(Conflict.lga_rel),
        joinedload(Conflict.actor_1_rel),
        joinedload(Conflict.actor_2_rel),
        joinedload(Conflict.actor_3_rel),
    )
    
    # Apply filters
    if start_date:
        query = query.filter(Conflict.incidence_date >= start_date)
    if end_date:
        query = query.filter(Conflict.incidence_date <= end_date)
    
    if region_id:
        query = query.filter(Conflict.region_id == region_id)
    if state_id:
        query = query.filter(Conflict.state_id == state_id)
    if lga_id:
        query = query.filter(Conflict.lga_id == lga_id)
    if community:
        query = query.filter(Conflict.community.ilike(f"%{community}%"))
    
    if conflict_type_id:
        query = query.filter(Conflict.conflict_type_id == conflict_type_id)
    
    if actor_id:
        query = query.filter(
            or_(
                Conflict.actor_1 == actor_id,
                Conflict.actor_2 == actor_id,
                Conflict.actor_3 == actor_id,
            )
        )
    
    if verification_level:
        query = query.filter(Conflict.verification_level == verification_level)
    
    # Exclude soft-deleted
    query = query.filter(Conflict.deleted_at.is_(None))
    
    # Sorting
    if sort_by == "total_deaths":
        # Computed column: sum of all death categories
        total_deaths_expr = (
            Conflict.civilian_death_male +
            Conflict.civilian_death_female +
            Conflict.civilian_death_unknown +
            Conflict.security_death_male +
            Conflict.security_death_female +
            Conflict.security_death_unknown
        )
        if sort_order == "desc":
            query = query.order_by(total_deaths_expr.desc())
        else:
            query = query.order_by(total_deaths_expr.asc())
    else:
        order_col = getattr(Conflict, sort_by)
        if sort_order == "desc":
            query = query.order_by(order_col.desc())
        else:
            query = query.order_by(order_col.asc())
    
    # Pagination
    conflicts = query.offset(skip).limit(limit).all()
    
    # Enrich with computed totals
    result = []
    for c in conflicts:
        conflict_dict = schemas.Conflict.model_validate(c).model_dump()
        
        # Add joined reference data
        conflict_dict["conflict_type"] = c.conflict_type_rel
        conflict_dict["region"] = c.region_rel
        conflict_dict["state"] = c.state_rel
        conflict_dict["lga"] = c.lga_rel
        conflict_dict["actor_1_obj"] = c.actor_1_rel
        conflict_dict["actor_2_obj"] = c.actor_2_rel
        conflict_dict["actor_3_obj"] = c.actor_3_rel
        
        # Compute totals
        conflict_dict["total_deaths"] = (
            c.civilian_death_male + c.civilian_death_female + c.civilian_death_unknown +
            c.security_death_male + c.security_death_female + c.security_death_unknown
        )
        conflict_dict["total_civilian_deaths"] = (
            c.civilian_death_male + c.civilian_death_female + c.civilian_death_unknown
        )
        conflict_dict["total_security_deaths"] = (
            c.security_death_male + c.security_death_female + c.security_death_unknown
        )
        conflict_dict["total_injured"] = (
            c.injured_male + c.injured_female + c.injured_unknown
        )
        conflict_dict["total_kidnapped"] = (
            c.kidnapped_male + c.kidnapped_female + c.kidnapped_unknown
        )
        conflict_dict["total_displaced"] = c.displaced_male + c.displaced_female
        
        result.append(schemas.ConflictWithDetails(**conflict_dict))
    
    return result


@router.get("/summary", response_model=List[schemas.ConflictSummary])
def list_conflicts_summary(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(500, ge=1, le=5000),
    
    # Same filters as list_conflicts
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    region_id: Optional[int] = None,
    state_id: Optional[int] = None,
    lga_id: Optional[int] = None,
    conflict_type_id: Optional[int] = None,
    actor_id: Optional[int] = None,
):
    """
    Lightweight conflict summaries for map/dashboard display.
    Returns minimal fields with computed totals (no full details).
    """
    query = db.query(
        Conflict.id,
        Conflict.incidence_date,
        Conflict.state_id,
        State.title.label("state_name"),
        LGA.title.label("lga_name"),
        Conflict.community,
        ConflictType.title.label("conflict_type_name"),
        Conflict.verification_level,
        (
            Conflict.civilian_death_male + Conflict.civilian_death_female + Conflict.civilian_death_unknown +
            Conflict.security_death_male + Conflict.security_death_female + Conflict.security_death_unknown
        ).label("total_deaths"),
        (
            Conflict.injured_male + Conflict.injured_female + Conflict.injured_unknown
        ).label("total_injured"),
    ).outerjoin(State, Conflict.state_id == State.id) \
     .outerjoin(LGA, Conflict.lga_id == LGA.id) \
     .outerjoin(ConflictType, Conflict.conflict_type_id == ConflictType.id)
    
    # Apply filters
    if start_date:
        query = query.filter(Conflict.incidence_date >= start_date)
    if end_date:
        query = query.filter(Conflict.incidence_date <= end_date)
    if region_id:
        query = query.filter(Conflict.region_id == region_id)
    if state_id:
        query = query.filter(Conflict.state_id == state_id)
    if lga_id:
        query = query.filter(Conflict.lga_id == lga_id)
    if conflict_type_id:
        query = query.filter(Conflict.conflict_type_id == conflict_type_id)
    if actor_id:
        query = query.filter(
            or_(
                Conflict.actor_1 == actor_id,
                Conflict.actor_2 == actor_id,
                Conflict.actor_3 == actor_id,
            )
        )
    
    query = query.filter(Conflict.deleted_at.is_(None))
    
    # Order by date descending
    query = query.order_by(Conflict.incidence_date.desc())
    
    # Pagination
    return query.offset(skip).limit(limit).all()


@router.get("/stats", response_model=schemas.ConflictStats)
def get_conflict_stats(
    db: Session = Depends(deps.get_db),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    state_id: Optional[int] = None,
    conflict_type_id: Optional[int] = None,
):
    """
    Aggregate statistics across conflicts.
    """
    # Base query
    query = db.query(Conflict).filter(Conflict.deleted_at.is_(None))
    
    if start_date:
        query = query.filter(Conflict.incidence_date >= start_date)
    if end_date:
        query = query.filter(Conflict.incidence_date <= end_date)
    if state_id:
        query = query.filter(Conflict.state_id == state_id)
    if conflict_type_id:
        query = query.filter(Conflict.conflict_type_id == conflict_type_id)
    
    # Count and sums
    stats = query.with_entities(
        func.count(Conflict.id).label("total_conflicts"),
        func.sum(
            Conflict.civilian_death_male + Conflict.civilian_death_female + Conflict.civilian_death_unknown +
            Conflict.security_death_male + Conflict.security_death_female + Conflict.security_death_unknown
        ).label("total_deaths"),
        func.sum(
            Conflict.injured_male + Conflict.injured_female + Conflict.injured_unknown
        ).label("total_injured"),
        func.sum(
            Conflict.kidnapped_male + Conflict.kidnapped_female + Conflict.kidnapped_unknown
        ).label("total_kidnapped"),
        func.sum(
            Conflict.displaced_male + Conflict.displaced_female
        ).label("total_displaced"),
        func.min(Conflict.incidence_date).label("date_range_start"),
        func.max(Conflict.incidence_date).label("date_range_end"),
    ).first()
    
    # By state breakdown
    by_state = {}
    if not state_id:  # Only compute if not already filtered by state
        state_stats = db.query(
            State.title,
            func.count(Conflict.id).label("count")
        ).join(Conflict, Conflict.state_id == State.id) \
         .filter(Conflict.deleted_at.is_(None))
        
        if start_date:
            state_stats = state_stats.filter(Conflict.incidence_date >= start_date)
        if end_date:
            state_stats = state_stats.filter(Conflict.incidence_date <= end_date)
        
        state_stats = state_stats.group_by(State.title).all()
        by_state = {row.title: row.count for row in state_stats}
    
    # By conflict type breakdown
    by_conflict_type = {}
    if not conflict_type_id:
        type_stats = db.query(
            ConflictType.title,
            func.count(Conflict.id).label("count")
        ).join(Conflict, Conflict.conflict_type_id == ConflictType.id) \
         .filter(Conflict.deleted_at.is_(None))
        
        if start_date:
            type_stats = type_stats.filter(Conflict.incidence_date >= start_date)
        if end_date:
            type_stats = type_stats.filter(Conflict.incidence_date <= end_date)
        
        type_stats = type_stats.group_by(ConflictType.title).all()
        by_conflict_type = {row.title: row.count for row in type_stats}
    
    return schemas.ConflictStats(
        total_conflicts=stats.total_conflicts or 0,
        total_deaths=stats.total_deaths or 0,
        total_injured=stats.total_injured or 0,
        total_kidnapped=stats.total_kidnapped or 0,
        total_displaced=stats.total_displaced or 0,
        date_range_start=stats.date_range_start,
        date_range_end=stats.date_range_end,
        by_state=by_state if by_state else None,
        by_conflict_type=by_conflict_type if by_conflict_type else None,
    )


@router.get("/{conflict_id}", response_model=schemas.ConflictWithDetails)
def get_conflict(
    conflict_id: int,
    db: Session = Depends(deps.get_db),
):
    """
    Get single conflict by ID (BIGSERIAL, not UUID).
    """
    conflict = db.query(Conflict).options(
        joinedload(Conflict.conflict_type_rel),
        joinedload(Conflict.region_rel),
        joinedload(Conflict.state_rel),
        joinedload(Conflict.lga_rel),
        joinedload(Conflict.actor_1_rel),
        joinedload(Conflict.actor_2_rel),
        joinedload(Conflict.actor_3_rel),
    ).filter(
        Conflict.id == conflict_id,
        Conflict.deleted_at.is_(None)
    ).first()
    
    if not conflict:
        raise HTTPException(status_code=404, detail=f"Conflict {conflict_id} not found")
    
    # Build response with computed totals
    conflict_dict = schemas.Conflict.model_validate(conflict).model_dump()
    conflict_dict["conflict_type"] = conflict.conflict_type_rel
    conflict_dict["region"] = conflict.region_rel
    conflict_dict["state"] = conflict.state_rel
    conflict_dict["lga"] = conflict.lga_rel
    conflict_dict["actor_1_obj"] = conflict.actor_1_rel
    conflict_dict["actor_2_obj"] = conflict.actor_2_rel
    conflict_dict["actor_3_obj"] = conflict.actor_3_rel
    
    conflict_dict["total_deaths"] = (
        conflict.civilian_death_male + conflict.civilian_death_female + conflict.civilian_death_unknown +
        conflict.security_death_male + conflict.security_death_female + conflict.security_death_unknown
    )
    conflict_dict["total_civilian_deaths"] = (
        conflict.civilian_death_male + conflict.civilian_death_female + conflict.civilian_death_unknown
    )
    conflict_dict["total_security_deaths"] = (
        conflict.security_death_male + conflict.security_death_female + conflict.security_death_unknown
    )
    conflict_dict["total_injured"] = (
        conflict.injured_male + conflict.injured_female + conflict.injured_unknown
    )
    conflict_dict["total_kidnapped"] = (
        conflict.kidnapped_male + conflict.kidnapped_female + conflict.kidnapped_unknown
    )
    conflict_dict["total_displaced"] = conflict.displaced_male + conflict.displaced_female
    
    return schemas.ConflictWithDetails(**conflict_dict)


@router.post("/", response_model=schemas.Conflict)
def create_conflict(
    conflict_in: schemas.ConflictCreate,
    db: Session = Depends(deps.get_db),
    # current_user = Depends(deps.require_role(["analyst", "admin"]))  # Uncomment when auth ready
):
    """
    Create new conflict record (analyst/admin only).
    """
    # Validate foreign keys exist
    if conflict_in.conflict_type_id:
        ct = db.query(ConflictType).filter(ConflictType.id == conflict_in.conflict_type_id).first()
        if not ct:
            raise HTTPException(status_code=400, detail=f"Conflict type {conflict_in.conflict_type_id} not found")
    
    if conflict_in.state_id:
        state = db.query(State).filter(State.id == conflict_in.state_id).first()
        if not state:
            raise HTTPException(status_code=400, detail=f"State {conflict_in.state_id} not found")
        # Auto-set region_id from state
        if not conflict_in.region_id and state.region_id:
            conflict_in.region_id = state.region_id
    
    if conflict_in.lga_id:
        lga = db.query(LGA).filter(LGA.id == conflict_in.lga_id).first()
        if not lga:
            raise HTTPException(status_code=400, detail=f"LGA {conflict_in.lga_id} not found")
    
    for actor_field in ["actor_1", "actor_2", "actor_3"]:
        actor_id = getattr(conflict_in, actor_field)
        if actor_id:
            actor = db.query(Actor).filter(Actor.id == actor_id).first()
            if not actor:
                raise HTTPException(status_code=400, detail=f"Actor {actor_id} not found")
    
    # Create conflict
    conflict = Conflict(**conflict_in.model_dump())
    db.add(conflict)
    db.commit()
    db.refresh(conflict)
    
    return conflict


@router.put("/{conflict_id}", response_model=schemas.Conflict)
def update_conflict(
    conflict_id: int,
    conflict_in: schemas.ConflictUpdate,
    db: Session = Depends(deps.get_db),
    # current_user = Depends(deps.require_role(["analyst", "admin"]))
):
    """
    Update conflict record (analyst/admin only).
    """
    conflict = db.query(Conflict).filter(
        Conflict.id == conflict_id,
        Conflict.deleted_at.is_(None)
    ).first()
    
    if not conflict:
        raise HTTPException(status_code=404, detail=f"Conflict {conflict_id} not found")
    
    # Update fields (only non-None values)
    update_data = conflict_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(conflict, field, value)
    
    db.commit()
    db.refresh(conflict)
    
    return conflict


@router.delete("/{conflict_id}")
def delete_conflict(
    conflict_id: int,
    db: Session = Depends(deps.get_db),
    # current_user = Depends(deps.require_role(["admin"]))
):
    """
    Soft-delete conflict record (admin only).
    """
    conflict = db.query(Conflict).filter(
        Conflict.id == conflict_id,
        Conflict.deleted_at.is_(None)
    ).first()
    
    if not conflict:
        raise HTTPException(status_code=404, detail=f"Conflict {conflict_id} not found")
    
    # Soft delete
    conflict.deleted_at = datetime.utcnow()
    db.commit()
    
    return {"status": "deleted", "id": conflict_id}


# Reference data endpoints
@router.get("/reference/actors", response_model=List[schemas.Actor])
def list_actors(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
):
    """List all actors (armed groups, security forces, civilians)."""
    return db.query(Actor).order_by(Actor.title).offset(skip).limit(limit).all()


@router.get("/reference/conflict-types", response_model=List[schemas.ConflictType])
def list_conflict_types(
    db: Session = Depends(deps.get_db),
):
    """List all conflict types (terrorism, banditry, farmer-herder, etc.)."""
    return db.query(ConflictType).order_by(ConflictType.title).all()


@router.get("/reference/regions", response_model=List[schemas.Region])
def list_regions(
    db: Session = Depends(deps.get_db),
):
    """List all regions (6 geo-political zones)."""
    return db.query(Region).order_by(Region.name).all()


@router.get("/reference/states", response_model=List[schemas.State])
def list_states(
    db: Session = Depends(deps.get_db),
    region_id: Optional[int] = None,
):
    """List all states (optionally filtered by region)."""
    query = db.query(State)
    if region_id:
        query = query.filter(State.region_id == region_id)
    return query.order_by(State.title).all()


@router.get("/reference/lgas", response_model=List[schemas.LGA])
def list_lgas(
    db: Session = Depends(deps.get_db),
    state_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 1000,
):
    """List all LGAs (optionally filtered by state)."""
    query = db.query(LGA)
    if state_id:
        query = query.filter(LGA.state_id == state_id)
    return query.order_by(LGA.title).offset(skip).limit(limit).all()
