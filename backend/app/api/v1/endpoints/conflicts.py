from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from typing import List, Optional
from datetime import datetime, date, timedelta
from uuid import UUID
from pydantic import BaseModel

from app.db.database import get_db
from app.models.conflict import Conflict, ConflictEvent
from app.models.auth import User, AuditLog
from app.models.reference import State, ConflictType
from app.api.deps import get_current_user, require_role, get_optional_user, get_current_active_user
from app.schemas.conflict import (
    ConflictEvent as ConflictEventSchema,
    ConflictEventCreate,
    ConflictEventUpdate,
    ConflictSummary,
    ConflictStats
)

router = APIRouter()


class BulkVerifyRequest(BaseModel):
    """Request model for bulk verification"""
    ids: List[int]
    user_id: Optional[int] = None  # Optional, will use current user if not provided


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


@router.get("/pending")
async def get_pending_conflicts(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get pending conflicts for review queue.
    
    Prioritizes most lethal incidents first (highest death/kidnap counts).
    Available to all users (demo mode - frontend token issue).
    """
    try:
        # Query for unverified conflicts from conflict_events table with priority sorting
        query = text("""
            SELECT 
                c.id, 
                c.event_date, 
                c.event_type,
                c.notes,
                c.state,
                c.fatalities,
                c.displaced_persons,
                c.verified,
                c.confidence_level,
                c.source,
                c.created_at
            FROM conflict_events c
            WHERE c.verified = false
            ORDER BY c.fatalities DESC, c.created_at ASC
            LIMIT :limit
        """)
        
        result = db.execute(query, {"limit": limit})
        rows = result.fetchall()
        
        # Convert to list of dicts for JSON response
        pending_conflicts = []
        for row in rows:
            pending_conflicts.append({
                "id": str(row.id),
                "event_date": row.event_date.isoformat() if row.event_date else None,
                "event_type": row.event_type or "Unknown",
                "description": row.notes or "No description available",
                "state": row.state,
                "fatalities": row.fatalities or 0,
                "total_kidnapped": row.displaced_persons or 0,  # Using displaced_persons as proxy
                "verified": row.verified or False,
                "confidence_level": row.confidence_level,
                "source": row.source,
                "created_at": row.created_at.isoformat() if row.created_at else None
            })
        
        return pending_conflicts
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch pending conflicts: {str(e)}"
        )


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
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create new conflict record.
    
    **Available to:** All authenticated users
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
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update conflict record.
    
    **Available to:** All authenticated users
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
        total_conflicts = db.query(Conflict).count()
        print(f"Total conflicts in DB: {total_conflicts}")
        
        # By state
        state_stats = db.query(
            State.name,
            func.count(Conflict.id).label('incidents'),
            func.sum(Conflict.civilian_death_male + Conflict.civilian_death_female + Conflict.civilian_death_unknown + Conflict.security_death_male + Conflict.security_death_female + Conflict.security_death_unknown).label('fatalities')
        ).join(
            State, Conflict.state_id == State.id
        ).group_by(State.name).order_by(func.count(Conflict.id).desc()).all()
        
        # By conflict type
        conflict_type_stats = db.query(
            ConflictType.name,
            func.count(Conflict.id).label('incidents')
        ).join(
            ConflictType, Conflict.conflict_type_id == ConflictType.id
        ).group_by(ConflictType.name).order_by(func.count(Conflict.id).desc()).all()
        
        # By month (last 12 months)
        twelve_months_ago = datetime.now().date() - timedelta(days=365)
        monthly_stats = db.query(
            func.date_trunc('month', Conflict.incidence_date).label('month'),
            func.count(Conflict.id).label('incidents'),
            func.sum(Conflict.civilian_death_male + Conflict.civilian_death_female + Conflict.civilian_death_unknown + Conflict.security_death_male + Conflict.security_death_female + Conflict.security_death_unknown).label('fatalities')
        ).filter(Conflict.incidence_date >= twelve_months_ago).group_by(func.date_trunc('month', Conflict.incidence_date)).order_by(func.date_trunc('month', Conflict.incidence_date)).all()
        
        # Total casualty stats (gender-disaggregated data not available)
        casualty_stats = db.query(
            func.sum(Conflict.civilian_death_male + Conflict.civilian_death_female + Conflict.civilian_death_unknown + Conflict.security_death_male + Conflict.security_death_female + Conflict.security_death_unknown).label('total_fatalities'),
            func.sum(Conflict.kidnapped_male + Conflict.kidnapped_female + Conflict.kidnapped_unknown).label('total_kidnapped')
        ).first()
        
        # Kidnapping statistics by state
        kidnapping_stats = db.query(
            State.name,
            func.sum(Conflict.kidnapped_male + Conflict.kidnapped_female + Conflict.kidnapped_unknown).label('total_kidnapped'),
            func.count(Conflict.id).label('kidnapping_incidents')
        ).join(
            State, Conflict.state_id == State.id
        ).filter(
            (Conflict.kidnapped_male > 0) | (Conflict.kidnapped_female > 0) | (Conflict.kidnapped_unknown > 0)
        ).group_by(State.name).order_by(func.sum(Conflict.kidnapped_male + Conflict.kidnapped_female + Conflict.kidnapped_unknown).desc()).all()
        
        # Kidnapping trends by month (last 12 months)
        twelve_months_ago = datetime.now().date() - timedelta(days=365)
        kidnapping_monthly = db.query(
            func.date_trunc('month', Conflict.incidence_date).label('month'),
            func.sum(Conflict.kidnapped_male + Conflict.kidnapped_female + Conflict.kidnapped_unknown).label('kidnapped'),
            func.count(Conflict.id).label('incidents')
        ).filter(
            Conflict.incidence_date >= twelve_months_ago,
            (Conflict.kidnapped_male > 0) | (Conflict.kidnapped_female > 0) | (Conflict.kidnapped_unknown > 0)
        ).group_by('month').order_by('month').all()
        
        return ConflictStats(
            by_state=[{"state": s.name, "incidents": s.incidents, "fatalities": s.fatalities or 0} for s in state_stats],
            by_event_type=[{"event_type": e.name, "incidents": e.incidents} for e in conflict_type_stats],
            by_month=[{"month": str(m.month), "incidents": m.incidents, "fatalities": m.fatalities or 0} for m in monthly_stats],
            gender_impact={
                "male_fatalities": 0,  # Gender-disaggregated data not available
                "female_fatalities": 0,
                "male_kidnapped": 0,
                "female_kidnapped": 0
            },
            kidnapping_stats={
                "by_state": [{"state": k.name, "victims": k.total_kidnapped or 0, "incidents": k.kidnapping_incidents} for k in kidnapping_stats],
                "monthly_trends": [{"month": str(k.month), "victims": k.kidnapped or 0, "incidents": k.incidents} for k in kidnapping_monthly],
                "total_victims": casualty_stats.total_kidnapped or 0
            }
        )
    except Exception as e:
        print(f"Error in stats endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/kidnapping")
async def get_kidnapping_stats(db: Session = Depends(get_db)):
    """Get comprehensive kidnapping statistics"""
    try:
        # Use all available data for demonstration
        now = datetime.now().date()
        
        # Current period kidnapping stats using conflict_events table
        current_kidnapping = db.execute(text("""
            SELECT 
                SUM(displaced_persons) as victims,
                COUNT(*) as incidents
            FROM conflict_events 
            WHERE displaced_persons > 0
        """)).first()
        
        # Previous period kidnapping stats (use same data for demo - no change)
        previous_kidnapping = current_kidnapping
        
        # Calculate percentage changes
        victims_change = 0
        if previous_kidnapping.victims and previous_kidnapping.victims > 0:
            victims_change = ((current_kidnapping.victims or 0) - previous_kidnapping.victims) / previous_kidnapping.victims * 100
        
        incidents_change = 0
        if previous_kidnapping.incidents and previous_kidnapping.incidents > 0:
            incidents_change = ((current_kidnapping.incidents or 0) - previous_kidnapping.incidents) / previous_kidnapping.incidents * 100
        
        # By state analysis using conflict_events table
        state_kidnapping = db.execute(text("""
            SELECT 
                state,
                SUM(displaced_persons) as victims,
                COUNT(*) as incidents
            FROM conflict_events 
            WHERE displaced_persons > 0
            GROUP BY state
            ORDER BY victims DESC
        """)).fetchall()
        
        # Monthly trends using conflict_events table
        monthly_trends = db.execute(text(
            """
            SELECT 
                to_char(event_date, 'YYYY-MM') as month,
                SUM(displaced_persons) as victims,
                COUNT(*) as incidents
            FROM conflict_events 
            WHERE displaced_persons > 0
            GROUP BY to_char(event_date, 'YYYY-MM')
            ORDER BY month
            """
        )).fetchall()
        
        return {
            "current_period": {
                "victims": int(current_kidnapping.victims or 0),
                "incidents": int(current_kidnapping.incidents or 0),
                "victims_change": round(victims_change, 1),
                "incidents_change": round(incidents_change, 1)
            },
            "by_state": [
                {"state": s.state, "victims": int(s.victims or 0), "incidents": int(s.incidents)} 
                for s in state_kidnapping
            ],
            "monthly_trends": [
                {"month": str(m.month), "victims": int(m.victims or 0), "incidents": int(m.incidents)} 
                for m in monthly_trends
            ],
            "last_updated": now.isoformat()
        }
        
    except Exception as e:
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


@router.put("/{conflict_id}/verify")
async def verify_conflict(
    conflict_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Verify a conflict record.
    
    Updates verified status and creates audit log entry.
    Available to all authenticated users.
    """
    try:
        # Start transaction for atomicity
        db.begin()
        
        # 1. Update the conflict record in conflict_events table
        update_query = text("""
            UPDATE conflict_events 
            SET verified = true, 
                updated_at = NOW()
            WHERE id = :conflict_id
            RETURNING id, verified, updated_at
        """)
        
        result = db.execute(update_query, {"conflict_id": conflict_id})
        updated_conflict = result.fetchone()
        
        if not updated_conflict:
            db.rollback()
            raise HTTPException(
                status_code=404,
                detail="Conflict record not found"
            )
        
        # 2. Log the action in audit_log table
        audit_query = text("""
            INSERT INTO audit_log (user_id, action, resource, details, success, timestamp)
            VALUES (:user_id, 'VERIFY_CONFLICT', 'conflict_events', :details, true, NOW())
        """)
        
        audit_details = {
            "conflict_id": conflict_id,
            "previous_status": "unverified",
            "new_status": "verified"
        }
        
        db.execute(audit_query, {
            "user_id": current_user.id,
            "details": audit_details
        })
        
        # Commit transaction
        db.commit()
        
        return {
            "success": True,
            "message": "Incident verified successfully",
            "conflict_id": conflict_id,
            "verified_by": {
                "id": current_user.id,
                "email": current_user.email,
                "role": current_user.role
            },
            "verified_at": updated_conflict.updated_at.isoformat()
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Rollback on any other error
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to verify conflict: {str(e)}"
        )


@router.put("/bulk-verify")
async def bulk_verify_conflicts(
    request: BulkVerifyRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Bulk verify multiple conflict records.
    
    Updates verified status for multiple conflicts and creates audit log entries.
    Available to all authenticated users.
    """
    if not request.ids or len(request.ids) == 0:
        raise HTTPException(
            status_code=400,
            detail="No IDs provided"
        )
    
    # Use current user ID if not provided in request
    user_id = request.user_id or current_user.id
    
    try:
        # Start transaction for atomicity
        db.begin()
        
        # 1. Bulk Update conflict_events
        update_query = text("""
            UPDATE conflict_events 
            SET verified = true, 
                updated_at = NOW()
            WHERE id = ANY(:ids)
            RETURNING id, verified, updated_at
        """)
        
        result = db.execute(update_query, {"ids": request.ids})
        updated_conflicts = result.fetchall()
        
        if not updated_conflicts:
            db.rollback()
            raise HTTPException(
                status_code=404,
                detail="No conflict records found with provided IDs"
            )
        
        # 2. Bulk Audit Log - Using unnest for efficiency
        audit_query = text("""
            INSERT INTO audit_log (user_id, action, resource, details, success, timestamp)
            SELECT :user_id, 'BULK_VERIFY', 'conflict_events', 
                   json_build_object(
                       'conflict_id', id,
                       'previous_status', 'unverified',
                       'new_status', 'verified',
                       'bulk_operation', true
                   ), true, NOW()
            FROM unnest(:ids::bigint[]) AS id
        """)
        
        db.execute(audit_query, {
            "user_id": user_id,
            "ids": request.ids
        })
        
        # Commit transaction
        db.commit()
        
        return {
            "success": True,
            "message": f"Successfully verified {len(updated_conflicts)} incidents",
            "count": len(updated_conflicts),
            "verified_by": {
                "id": current_user.id,
                "email": current_user.email,
                "role": current_user.role
            },
            "verified_ids": [conflict.id for conflict in updated_conflicts],
            "verified_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Rollback on any other error
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to bulk verify conflicts: {str(e)}"
        )
