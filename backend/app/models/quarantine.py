"""
Data Quarantine Model for tracking validation failures and suspicious entries
"""

from sqlalchemy import Column, Integer, DateTime, String, Text, JSON, Boolean, Index, ForeignKey
from datetime import datetime
from app.db.base_class import Base


class DataQuarantine(Base):
    """Track events that fail validation or are flagged as suspicious"""
    
    __tablename__ = "data_quarantine"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Source information
    source = Column(String(100), nullable=False, index=True)  # 'news_scraper', 'excel_import', etc.
    source_url = Column(String(500))  # Original URL if from web scraper
    
    # Raw data that failed validation
    raw_data = Column(JSON, nullable=False)  # The complete original record
    
    # Validation failure details
    validation_status = Column(String(20), nullable=False, default='failed')  # 'failed', 'warning', 'pending'
    validation_issues = Column(JSON, nullable=False)  # List of issues found
    issue_count = Column(Integer, default=0)  # Number of validation issues
    
    # Classification for manual review
    quarantine_reason = Column(String(100))  # 'duplicate', 'invalid_data', 'suspicious_values', 'missing_fields'
    severity = Column(String(20))  # 'critical', 'warning'
    
    # Manual review status
    reviewed = Column(Boolean, default=False, index=True)
    reviewer_notes = Column(Text)  # Notes from manual review
    resolution_status = Column(String(20))  # 'pending', 'approved', 'rejected', 'corrected'
    
    # If approved/corrected, link to inserted record
    resolved_conflict_event_id = Column(String(100), index=True)  # UUID of the inserted event
    
    # Timeline
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)
    reviewed_at = Column(DateTime(timezone=True))
    resolved_at = Column(DateTime(timezone=True))
    
    # Indexes
    __table_args__ = (
        Index('idx_quarantine_source', 'source'),
        Index('idx_quarantine_reviewed', 'reviewed'),
        Index('idx_quarantine_status', 'resolution_status'),
        Index('idx_quarantine_created', 'created_at'),
        Index('idx_quarantine_severity', 'severity'),
    )
    
    def __repr__(self):
        return (
            f"<DataQuarantine(id={self.id}, source={self.source}, "
            f"reason={self.quarantine_reason}, status={self.resolution_status})>"
        )
