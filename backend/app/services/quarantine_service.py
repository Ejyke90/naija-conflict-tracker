"""
Quarantine Service - manages data validation failures and suspicious entries
Provides API for manual review and resolution
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from app.db.database import SessionLocal
from app.models.quarantine import DataQuarantine
from app.models.conflict import ConflictEvent
from sqlalchemy import desc
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class QuarantineService:
    """Manages quarantine records for data validation failures"""
    
    def __init__(self, db: Optional[Session] = None):
        self.db = db or SessionLocal()
    
    def add_to_quarantine(
        self,
        raw_data: Dict[str, Any],
        source: str,
        validation_issues: List[str],
        severity: str = "warning",
        source_url: Optional[str] = None,
        quarantine_reason: str = "validation_failed"
    ) -> DataQuarantine:
        """
        Add a record to quarantine for manual review
        
        Args:
            raw_data: The raw record data that failed validation
            source: Source of the data ('news_scraper', 'excel_import', etc.)
            validation_issues: List of validation issues found
            severity: 'critical' or 'warning'
            source_url: Original URL if applicable
            quarantine_reason: Reason for quarantine
        
        Returns:
            DataQuarantine record created
        """
        try:
            quarantine_record = DataQuarantine(
                source=source,
                source_url=source_url,
                raw_data=raw_data,
                validation_status='failed' if severity == 'critical' else 'warning',
                validation_issues=validation_issues,
                issue_count=len(validation_issues),
                quarantine_reason=quarantine_reason,
                severity=severity
            )
            
            self.db.add(quarantine_record)
            self.db.commit()
            self.db.refresh(quarantine_record)
            
            logger.info(
                f"Added record to quarantine: source={source}, "
                f"issues={len(validation_issues)}, severity={severity}"
            )
            
            return quarantine_record
        
        except Exception as e:
            logger.error(f"Failed to add record to quarantine: {e}")
            self.db.rollback()
            raise
    
    def get_quarantine_queue(
        self,
        reviewed: bool = False,
        severity: Optional[str] = None,
        source: Optional[str] = None,
        limit: int = 100
    ) -> List[DataQuarantine]:
        """Get records in quarantine queue for manual review"""
        try:
            query = self.db.query(DataQuarantine)
            
            if not reviewed:
                query = query.filter(DataQuarantine.reviewed == False)
            
            if severity:
                query = query.filter(DataQuarantine.severity == severity)
            
            if source:
                query = query.filter(DataQuarantine.source == source)
            
            return query.order_by(
                desc(DataQuarantine.severity),
                desc(DataQuarantine.created_at)
            ).limit(limit).all()
        
        except Exception as e:
            logger.error(f"Failed to get quarantine queue: {e}")
            return []
    
    def approve_quarantine_record(
        self,
        quarantine_id: int,
        reviewer_notes: str = ""
    ) -> bool:
        """
        Approve a quarantine record for insertion into the database
        
        This marks the record for processing but does not insert it.
        A separate worker should handle the actual insertion.
        """
        try:
            record = self.db.query(DataQuarantine).filter(
                DataQuarantine.id == quarantine_id
            ).first()
            
            if not record:
                logger.warning(f"Quarantine record {quarantine_id} not found")
                return False
            
            record.reviewed = True
            record.reviewed_at = datetime.utcnow()
            record.resolution_status = 'approved'
            record.reviewer_notes = reviewer_notes
            
            self.db.commit()
            logger.info(f"Approved quarantine record {quarantine_id}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to approve quarantine record: {e}")
            self.db.rollback()
            return False
    
    def reject_quarantine_record(
        self,
        quarantine_id: int,
        reviewer_notes: str = ""
    ) -> bool:
        """Reject a quarantine record (do not insert)"""
        try:
            record = self.db.query(DataQuarantine).filter(
                DataQuarantine.id == quarantine_id
            ).first()
            
            if not record:
                logger.warning(f"Quarantine record {quarantine_id} not found")
                return False
            
            record.reviewed = True
            record.reviewed_at = datetime.utcnow()
            record.resolution_status = 'rejected'
            record.reviewer_notes = reviewer_notes or "Data quality concerns"
            
            self.db.commit()
            logger.info(f"Rejected quarantine record {quarantine_id}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to reject quarantine record: {e}")
            self.db.rollback()
            return False
    
    def get_quarantine_stats(self) -> Dict[str, Any]:
        """Get statistics about quarantine queue"""
        try:
            total = self.db.query(DataQuarantine).count()
            pending_review = self.db.query(DataQuarantine).filter(
                DataQuarantine.reviewed == False
            ).count()
            critical = self.db.query(DataQuarantine).filter(
                DataQuarantine.severity == 'critical',
                DataQuarantine.reviewed == False
            ).count()
            approved = self.db.query(DataQuarantine).filter(
                DataQuarantine.resolution_status == 'approved'
            ).count()
            rejected = self.db.query(DataQuarantine).filter(
                DataQuarantine.resolution_status == 'rejected'
            ).count()
            
            return {
                "total_quarantined": total,
                "pending_review": pending_review,
                "critical_pending": critical,
                "approved": approved,
                "rejected": rejected,
                "review_rate": (
                    (approved + rejected) / total * 100 if total > 0 else 0
                )
            }
        
        except Exception as e:
            logger.error(f"Failed to get quarantine stats: {e}")
            return {}
    
    def mark_resolved(
        self,
        quarantine_id: int,
        resolved_event_id: str
    ) -> bool:
        """Mark a quarantine record as resolved (data was inserted)"""
        try:
            record = self.db.query(DataQuarantine).filter(
                DataQuarantine.id == quarantine_id
            ).first()
            
            if not record:
                return False
            
            record.resolution_status = 'corrected'
            record.resolved_at = datetime.utcnow()
            record.resolved_conflict_event_id = resolved_event_id
            
            self.db.commit()
            logger.info(f"Marked quarantine record {quarantine_id} as resolved")
            return True
        
        except Exception as e:
            logger.error(f"Failed to mark quarantine record as resolved: {e}")
            self.db.rollback()
            return False
    
    def get_recent_quarantine_by_source(self, source: str, days: int = 7) -> Dict[str, Any]:
        """Get quarantine statistics for a specific source in recent days"""
        from datetime import timedelta
        
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            records = self.db.query(DataQuarantine).filter(
                DataQuarantine.source == source,
                DataQuarantine.created_at >= cutoff_date
            ).all()
            
            total = len(records)
            critical = sum(1 for r in records if r.severity == 'critical')
            warning = sum(1 for r in records if r.severity == 'warning')
            approved = sum(1 for r in records if r.resolution_status == 'approved')
            
            return {
                "source": source,
                "period_days": days,
                "total_quarantined": total,
                "critical": critical,
                "warning": warning,
                "approved": approved,
                "approval_rate": (approved / total * 100) if total > 0 else 0
            }
        
        except Exception as e:
            logger.error(f"Failed to get quarantine stats by source: {e}")
            return {}
