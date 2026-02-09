"""
Conflict Event Insertion Service with Validation Integration
Handles inserting conflict events with data validation and quarantine
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from app.db.database import SessionLocal
from app.models.conflict import ConflictEvent
from app.services.data_validator import ConflictDataValidator
from app.services.quarantine_service import QuarantineService
from sqlalchemy.orm import Session
import uuid

logger = logging.getLogger(__name__)


class ConflictEventInsertionService:
    """Inserts conflict events with validation and quarantine support"""
    
    def __init__(self, db: Optional[Session] = None):
        self.db = db or SessionLocal()
        self.validator = ConflictDataValidator()
        self.quarantine_service = QuarantineService(self.db)
    
    def insert_with_validation(
        self,
        event_data: Dict[str, Any],
        source: str = "unknown",
        source_url: Optional[str] = None,
        allow_warnings: bool = False
    ) -> Tuple[bool, Optional[str], List[str]]:
        """
        Insert a conflict event with validation
        
        Args:
            event_data: Event data to insert
            source: Source of the data (news_scraper, excel_import, etc.)
            source_url: URL where data came from (if applicable)
            allow_warnings: If True, insert events with warnings; if False, send to quarantine
        
        Returns:
            (success: bool, conflict_event_id: Optional[str], issues: List[str])
        """
        # Step 1: Validate data
        is_valid, issues, severity = self.validator.validate(event_data)
        
        if not is_valid:
            # Handle validation failure
            if severity == "critical" or not allow_warnings:
                logger.warning(f"Validation failed for event from {source}: {issues}")
                
                # Send to quarantine
                quarantine_record = self.quarantine_service.add_to_quarantine(
                    raw_data=event_data,
                    source=source,
                    validation_issues=issues,
                    severity=severity or "warning",
                    source_url=source_url,
                    quarantine_reason="validation_failure"
                )
                
                return False, None, issues
        
        # Step 2: Insert into database
        try:
            # Parse event_date properly (could be string or datetime)
            event_date_raw = event_data.get("event_date")
            if isinstance(event_date_raw, str):
                from datetime import datetime
                event_date = datetime.strptime(event_date_raw, "%Y-%m-%d").date()
            else:
                event_date = event_date_raw
            
            conflict_event = ConflictEvent(
                id=str(uuid.uuid4()),
                event_date=event_date,
                year=event_date.year if event_date else None,
                month=event_date.month if event_date else None,
                event_type=event_data.get("event_type", "Unknown"),
                event_category=event_data.get("event_category"),
                conflict_type=event_data.get("conflict_type"),
                state=event_data.get("state"),
                lga=event_data.get("lga"),
                location=event_data.get("location"),
                latitude=event_data.get("latitude"),
                longitude=event_data.get("longitude"),
                actor1=event_data.get("actor1"),
                actor2=event_data.get("actor2"),
                actor1_type=event_data.get("actor1_type"),
                actor2_type=event_data.get("actor2_type"),
                fatalities=int(event_data.get("fatalities", 0)),
                injuries=int(event_data.get("injuries", 0)),
                properties_destroyed=int(event_data.get("properties_destroyed", 0)),
                displaced_persons=int(event_data.get("displaced_persons", 0)),
                source=source,
                notes=event_data.get("notes"),
                verified=event_data.get("verified", False),
                confidence_level=event_data.get("confidence_level", "Low")
            )
            
            self.db.add(conflict_event)
            self.db.commit()
            self.db.refresh(conflict_event)
            
            logger.info(f"Successfully inserted conflict event {conflict_event.id} from {source}")
            
            return True, str(conflict_event.id), issues
        
        except Exception as e:
            logger.error(f"Failed to insert conflict event: {e}")
            self.db.rollback()
            
            # Send to quarantine on insertion error
            self.quarantine_service.add_to_quarantine(
                raw_data=event_data,
                source=source,
                validation_issues=issues + [f"Insertion error: {str(e)}"],
                severity="critical",
                source_url=source_url,
                quarantine_reason="insertion_error"
            )
            
            return False, None, [str(e)]
    
    def batch_insert_with_validation(
        self,
        events: List[Dict[str, Any]],
        source: str = "unknown",
        allow_warnings: bool = False,
        stop_on_critical: bool = False
    ) -> Dict[str, Any]:
        """
        Insert multiple events with validation
        
        Args:
            events: List of event dictionaries
            source: Source of the data
            allow_warnings: Whether to allow events with warnings
            stop_on_critical: Stop processing on critical errors
        
        Returns:
            Statistics about insertion results
        """
        results = {
            "total": len(events),
            "inserted": 0,
            "quarantined": 0,
            "failed": 0,
            "duplicate_checks_failed": 0,
            "validation_issues_by_severity": {
                "critical": 0,
                "warning": 0
            },
            "successful_ids": [],
            "errors": []
        }
        
        for i, event_data in enumerate(events):
            try:
                success, event_id, issues = self.insert_with_validation(
                    event_data,
                    source=source,
                    allow_warnings=allow_warnings
                )
                
                if success:
                    results["inserted"] += 1
                    results["successful_ids"].append(event_id)
                else:
                    results["quarantined"] += 1
                    
                    # Check if critical
                    _, _, severity = self.validator.validate(event_data)
                    if severity == "critical":
                        results["validation_issues_by_severity"]["critical"] += 1
                        if stop_on_critical:
                            logger.warning(f"Stopping batch insert due to critical error at event {i+1}")
                            break
                    else:
                        results["validation_issues_by_severity"]["warning"] += 1
                
            except Exception as e:
                logger.error(f"Batch insert error at event {i+1}: {e}")
                results["failed"] += 1
                results["errors"].append(f"Event {i+1}: {str(e)}")
        
        results["duration"] = datetime.utcnow().isoformat()
        logger.info(
            f"Batch insert complete: {results['inserted']} inserted, "
            f"{results['quarantined']} quarantined, {results['failed']} failed"
        )
        
        return results
    
    def get_insertion_statistics(self, source: Optional[str] = None, days: int = 7) -> Dict[str, Any]:
        """Get statistics about recent insertions"""
        from datetime import timedelta
        
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            query = self.db.query(ConflictEvent).filter(
                ConflictEvent.created_at >= cutoff_date
            )
            
            if source:
                query = query.filter(ConflictEvent.source == source)
            
            total = query.count()
            verified = query.filter(ConflictEvent.verified == True).count()
            
            # Get quarantine stats
            quarantine_stats = self.quarantine_service.get_quarantine_stats()
            
            return {
                "period_days": days,
                "total_inserted": total,
                "verified": verified,
                "pending_verification": total - verified,
                "source": source or "all",
                "quarantine_stats": quarantine_stats,
                "statistics_as_of": datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Failed to get insertion statistics: {e}")
            return {}
