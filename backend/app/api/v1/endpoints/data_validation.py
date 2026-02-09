"""
API Endpoints for Data Validation & Quarantine Management
Exposes data validation and quarantine operations to admin users
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime
from app.services.data_validator import ConflictDataValidator
from app.services.quarantine_service import QuarantineService
from app.services.insertion_service import ConflictEventInsertionService
from app.db.database import SessionLocal
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/v1/data", tags=["data_validation"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============================================================================
# VALIDATION ENDPOINTS
# ============================================================================

@router.post("/validate-conflict")
async def validate_conflict_event(
    event_data: dict,
    db: Session = Depends(get_db)
):
    """
    Validate a single conflict event
    
    Returns validation status and any issues found
    """
    validator = ConflictDataValidator()
    is_valid, issues, severity = validator.validate(event_data)
    
    return {
        "is_valid": is_valid,
        "severity": severity,
        "issues": issues,
        "issue_count": len(issues)
    }

@router.post("/validate-batch")
async def validate_batch(
    events: List[dict],
    db: Session = Depends(get_db)
):
    """Validate a batch of events"""
    validator = ConflictDataValidator()
    
    results = []
    for event in events:
        is_valid, issues, severity = validator.validate(event)
        results.append({
            "event": event,
            "is_valid": is_valid,
            "severity": severity,
            "issues": issues
        })
    
    summary = validator.get_validation_summary(
        [(r["is_valid"], r["issues"], r["severity"]) for r in results]
    )
    
    return {
        "results": results,
        "summary": summary
    }

# ============================================================================
# QUARANTINE ENDPOINTS
# ============================================================================

@router.get("/quarantine/queue")
async def get_quarantine_queue(
    reviewed: bool = Query(False, description="Get reviewed or unreviewed items"),
    severity: Optional[str] = Query(None, description="Filter by severity (critical, warning)"),
    source: Optional[str] = Query(None, description="Filter by source"),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """
    Get the quarantine queue for manual review
    
    Returns items that failed validation
    """
    quarantine_service = QuarantineService(db)
    items = quarantine_service.get_quarantine_queue(
        reviewed=reviewed,
        severity=severity,
        source=source,
        limit=limit
    )
    
    return {
        "count": len(items),
        "items": [
            {
                "id": item.id,
                "source": item.source,
                "severity": item.severity,
                "reason": item.quarantine_reason,
                "issues": item.validation_issues,
                "issue_count": item.issue_count,
                "reviewed": item.reviewed,
                "created_at": item.created_at.isoformat() if item.created_at else None,
                "raw_data": item.raw_data
            }
            for item in items
        ]
    }

@router.get("/quarantine/stats")
async def get_quarantine_stats(
    db: Session = Depends(get_db)
):
    """Get quarantine queue statistics"""
    quarantine_service = QuarantineService(db)
    stats = quarantine_service.get_quarantine_stats()
    
    return stats

@router.get("/quarantine/{quarantine_id}")
async def get_quarantine_item(
    quarantine_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific quarantine item details"""
    quarantine_service = QuarantineService(db)
    
    from app.models.quarantine import DataQuarantine
    item = db.query(DataQuarantine).filter(
        DataQuarantine.id == quarantine_id
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Quarantine item not found")
    
    return {
        "id": item.id,
        "source": item.source,
        "source_url": item.source_url,
        "severity": item.severity,
        "reason": item.quarantine_reason,
        "issues": item.validation_issues,
        "reviewed": item.reviewed,
        "resolution_status": item.resolution_status,
        "reviewer_notes": item.reviewer_notes,
        "raw_data": item.raw_data,
        "created_at": item.created_at.isoformat() if item.created_at else None,
        "reviewed_at": item.reviewed_at.isoformat() if item.reviewed_at else None
    }

@router.post("/quarantine/{quarantine_id}/approve")
async def approve_quarantine_item(
    quarantine_id: int,
    reviewer_notes: str = "",
    db: Session = Depends(get_db)
):
    """Approve a quarantine item for insertion"""
    quarantine_service = QuarantineService(db)
    success = quarantine_service.approve_quarantine_record(
        quarantine_id,
        reviewer_notes
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Quarantine item not found")
    
    return {"status": "approved", "id": quarantine_id}

@router.post("/quarantine/{quarantine_id}/reject")
async def reject_quarantine_item(
    quarantine_id: int,
    reviewer_notes: str = "",
    db: Session = Depends(get_db)
):
    """Reject a quarantine item (do not insert)"""
    quarantine_service = QuarantineService(db)
    success = quarantine_service.reject_quarantine_record(
        quarantine_id,
        reviewer_notes
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Quarantine item not found")
    
    return {"status": "rejected", "id": quarantine_id}

@router.post("/quarantine/{quarantine_id}/insert")
async def insert_approved_quarantine(
    quarantine_id: int,
    db: Session = Depends(get_db)
):
    """Insert an approved quarantine item into the database"""
    from app.models.quarantine import DataQuarantine
    
    quarantine_item = db.query(DataQuarantine).filter(
        DataQuarantine.id == quarantine_id
    ).first()
    
    if not quarantine_item:
        raise HTTPException(status_code=404, detail="Quarantine item not found")
    
    if quarantine_item.resolution_status != "approved":
        raise HTTPException(
            status_code=400,
            detail=f"Can only insert approved items. Current status: {quarantine_item.resolution_status}"
        )
    
    # Insert using the insertion service
    insertion_service = ConflictEventInsertionService(db)
    success, event_id, issues = insertion_service.insert_with_validation(
        quarantine_item.raw_data,
        source=quarantine_item.source,
        source_url=quarantine_item.source_url,
        allow_warnings=True
    )
    
    if success:
        # Mark quarantine record as resolved
        quarantine_service = QuarantineService(db)
        quarantine_service.mark_resolved(quarantine_id, event_id)
        
        return {
            "status": "inserted",
            "conflict_event_id": event_id,
            "quarantine_id": quarantine_id
        }
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to insert: {', '.join(issues)}"
        )

# ============================================================================
# INSERTION ENDPOINTS
# ============================================================================

@router.post("/insert-conflict")
async def insert_conflict_event(
    event_data: dict,
    source: str = "api",
    allow_warnings: bool = False,
    db: Session = Depends(get_db)
):
    """
    Insert a single conflict event with validation
    
    Returns event ID if successful, sends to quarantine if validation fails
    """
    insertion_service = ConflictEventInsertionService(db)
    success, event_id, issues = insertion_service.insert_with_validation(
        event_data,
        source=source,
        allow_warnings=allow_warnings
    )
    
    if success:
        return {
            "status": "inserted",
            "event_id": event_id,
            "issues": issues
        }
    else:
        return {
            "status": "quarantined",
            "message": "Event failed validation and was sent to quarantine for review",
            "issues": issues
        }, 400

@router.get("/insertion-stats")
async def get_insertion_stats(
    source: Optional[str] = Query(None),
    days: int = Query(7, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Get statistics about recent insertions and validation"""
    insertion_service = ConflictEventInsertionService(db)
    stats = insertion_service.get_insertion_statistics(source, days)
    
    return stats

# ============================================================================
# DATA QUALITY MONITORING
# ============================================================================

@router.get("/quality-report")
async def get_data_quality_report(
    source: Optional[str] = Query(None),
    days: int = Query(7, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """
    Get a comprehensive data quality report
    
    Includes validation pass rates, quarantine stats, and insertion stats
    """
    insertion_service = ConflictEventInsertionService(db)
    quarantine_service = QuarantineService(db)
    
    insertion_stats = insertion_service.get_insertion_statistics(source, days)
    quarantine_stats = quarantine_service.get_quarantine_stats()
    
    if source:
        source_quarantine_stats = quarantine_service.get_recent_quarantine_by_source(source, days)
    else:
        source_quarantine_stats = None
    
    return {
        "insertion_stats": insertion_stats,
        "quarantine_stats": quarantine_stats,
        "source_specific_stats": source_quarantine_stats,
        "report_date": datetime.utcnow().isoformat()
    }
