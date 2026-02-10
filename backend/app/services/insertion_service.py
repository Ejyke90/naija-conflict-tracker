"""
Conflict Event Insertion Service with Validation Integration
Handles inserting conflict events with data validation and quarantine
Works with the normalized 'conflicts' table (PostgreSQL production schema)
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, date
from app.db.database import SessionLocal
from app.models.conflict import Conflict
from app.models.reference import State, ConflictType
from app.models.actor import Actor
from app.services.data_validator import ConflictDataValidator
from app.services.quarantine_service import QuarantineService
from sqlalchemy.orm import Session
from sqlalchemy import func
import uuid

logger = logging.getLogger(__name__)


class ConflictEventInsertionService:
    """Inserts conflict events with validation and quarantine support"""
    
    def __init__(self, db: Optional[Session] = None):
        self.db = db or SessionLocal()
        self.validator = ConflictDataValidator()
        try:
            self.quarantine_service = QuarantineService(self.db)
        except Exception as e:
            logger.warning(f"Quarantine service initialization failed: {e}. Quarantine will be disabled.")
            self.quarantine_service = None
    
    def _resolve_state_id(self, state_name: str) -> Optional[int]:
        """Resolve state name to state ID"""
        if not state_name:
            return None
        try:
            state = self.db.query(State).filter(
                func.lower(State.title) == func.lower(state_name)
            ).first()
            return state.id if state else None
        except Exception as e:
            logger.warning(f"Failed to resolve state {state_name}: {e}")
            return None
    
    def _resolve_actor_id(self, actor_name: str) -> Optional[int]:
        """Resolve actor name to actor ID"""
        if not actor_name:
            return None
        try:
            actor = self.db.query(Actor).filter(
                func.lower(Actor.name) == func.lower(actor_name)
            ).first()
            return actor.id if actor else None
        except Exception as e:
            logger.warning(f"Failed to resolve actor {actor_name}: {e}")
            return None
    
    def _parse_date(self, date_value: Any) -> Optional[date]:
        """Parse various date formats to Python date object"""
        if date_value is None:
            return None
        
        if isinstance(date_value, date):
            return date_value
        
        if isinstance(date_value, datetime):
            return date_value.date()
        
        if isinstance(date_value, str):
            try:
                return datetime.strptime(date_value, "%Y-%m-%d").date()
            except ValueError:
                logger.warning(f"Could not parse date: {date_value}")
                return None
        
        return None
    
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
                
                # Send to quarantine if service available
                if self.quarantine_service:
                    try:
                        self.quarantine_service.add_to_quarantine(
                            raw_data=event_data,
                            source=source,
                            validation_issues=issues,
                            severity=severity or "warning",
                            source_url=source_url,
                            quarantine_reason="validation_failure"
                        )
                    except Exception as e:
                        logger.error(f"Could not quarantine failed record: {e}")
                
                return False, None, issues
        
        # Step 2: Insert into database using normalized Conflict model
        try:
            # Parse event date
            event_date = self._parse_date(event_data.get("event_date"))
            if not event_date:
                raise ValueError("event_date is required and must be a valid date")
            
            # Resolve state ID from state name
            state_id = self._resolve_state_id(event_data.get("state"))
            if not state_id:
                raise ValueError(f"Could not resolve state: {event_data.get('state')}")
            
            # Resolve actor IDs from actor names
            actor_1_id = self._resolve_actor_id(event_data.get("actor1"))
            actor_2_id = self._resolve_actor_id(event_data.get("actor2"))
            actor_3_id = self._resolve_actor_id(event_data.get("actor3"))
            
            # Parse casualty numbers
            def parse_int(val, default=0):
                try:
                    return int(val) if val is not None else default
                except (ValueError, TypeError):
                    return default
            
            total_fatalities = parse_int(event_data.get("fatalities"), 0)
            total_injuries = parse_int(event_data.get("injuries"), 0)
            total_displaced = parse_int(event_data.get("displaced_persons"), 0)
            total_kidnapped = parse_int(event_data.get("kidnapped"), 0)
            
            # Create conflict record using normalized schema
            conflict = Conflict(
                incidence_date=event_date,
                state_id=state_id,
                community=event_data.get("location") or event_data.get("community"),
                
                # Disaggregated casualty data (use totals if gender breakdown not available)
                civilian_death_male=parse_int(event_data.get("civilian_death_male"), 0),
                civilian_death_female=parse_int(event_data.get("civilian_death_female"), 0),
                civilian_death_unknown=parse_int(event_data.get("civilian_death_unknown"), 
                                                 total_fatalities if not event_data.get("civilian_death_male") else 0),
                security_death_male=parse_int(event_data.get("security_death_male"), 0),
                security_death_female=parse_int(event_data.get("security_death_female"), 0),
                security_death_unknown=parse_int(event_data.get("security_death_unknown"), 0),
                
                # Injuries (without gender breakdown)
                injured_male=parse_int(event_data.get("injured_male"), 0),
                injured_female=parse_int(event_data.get("injured_female"), 0),
                injured_unknown=parse_int(event_data.get("injured_unknown"), 
                                          total_injuries if not event_data.get("injured_male") else 0),
                
                # Kidnapped (without gender breakdown)
                kidnapped_male=parse_int(event_data.get("kidnapped_male"), 0),
                kidnapped_female=parse_int(event_data.get("kidnapped_female"), 0),
                kidnapped_unknown=parse_int(event_data.get("kidnapped_unknown"), 
                                            total_kidnapped if not event_data.get("kidnapped_male") else 0),
                
                # Displaced persons
                displaced_persons=event_data.get("displaced_persons_yn", "No"),  # Yes/No flag
                displaced_male=parse_int(event_data.get("displaced_male"), 0),
                displaced_female=parse_int(event_data.get("displaced_female"), 0),
                
                # Actor references
                actor_1=actor_1_id,
                actor_2=actor_2_id,
                actor_3=actor_3_id,
                
                # Metadata
                description=event_data.get("description"),
                source_url=source_url,
                source_metadata=source,
                data_source=source,
                confirmation_verification=event_data.get("verification_level", "Unverified"),
                verification_level=event_data.get("verification_level", "Low")
            )
            
            self.db.add(conflict)
            self.db.commit()
            self.db.refresh(conflict)
            
            logger.info(f"Successfully inserted conflict ID {conflict.id} from {source}")
            
            return True, str(conflict.id), issues
        
        except Exception as e:
            logger.error(f"Failed to insert conflict event: {e}", exc_info=True)
            self.db.rollback()
            
            # Send to quarantine if service available
            if self.quarantine_service:
                try:
                    self.quarantine_service.add_to_quarantine(
                        raw_data=event_data,
                        source=source,
                        validation_issues=issues + [f"Insertion error: {str(e)}"],
                        severity="critical",
                        source_url=source_url,
                        quarantine_reason="insertion_error"
                    )
                except Exception as qe:
                    logger.error(f"Could not quarantine failed record: {qe}")
            
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
            
            # Query from Conflict model (normalized schema)
            query = self.db.query(Conflict).filter(
                Conflict.created_at >= cutoff_date
            )
            
            if source:
                query = query.filter(Conflict.data_source == source)
            
            total = query.count()
            verified = query.filter(
                Conflict.verification_level.in_(["High", "Verified"])
            ).count()
            
            # Get quarantine stats if service available
            quarantine_stats = {}
            if self.quarantine_service:
                try:
                    quarantine_stats = self.quarantine_service.get_quarantine_stats()
                except Exception as e:
                    logger.warning(f"Could not retrieve quarantine stats: {e}")
            
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
            return {
                "period_days": days,
                "total_inserted": 0,
                "verified": 0,
                "pending_verification": 0,
                "source": source or "all",
                "error": str(e),
                "statistics_as_of": datetime.utcnow().isoformat()
            }
