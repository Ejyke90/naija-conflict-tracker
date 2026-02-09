"""
Alert Event Model

Database model for high-risk conflict event alerts.
"""

from sqlalchemy import Column, Integer, String, Float, Text, TIMESTAMP, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class AlertEvent(Base):
    """High-risk conflict event alerts"""
    __tablename__ = "alert_events"
    
    id = Column(Integer, primary_key=True, index=True)
    conflict_event_id = Column(Integer, ForeignKey('conflict_events_new.id'), nullable=True)
    
    # Alert metadata
    alert_type = Column(String(20), nullable=False, index=True)  # HIGH, CRITICAL
    risk_score = Column(Float, nullable=False, index=True)
    priority = Column(Integer, nullable=False)  # 1=CRITICAL, 2=HIGH
    status = Column(String(20), default='ACTIVE', index=True)  # ACTIVE, ACKNOWLEDGED, RESOLVED, AUTO_RESOLVED
    
    # Location
    location_state = Column(String(100), index=True)
    location_lga = Column(String(100))
    
    # Event details
    conflict_category = Column(String(100))
    title = Column(Text, nullable=False)
    summary = Column(Text)
    
    # Deduplication
    dedup_key = Column(String(32), index=True)  # MD5 hash for deduplication
    
    # Acknowledgment tracking
    acknowledged_at = Column(TIMESTAMP)
    acknowledged_by_user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    acknowledgment_notes = Column(Text)
    
    # Resolution tracking
    resolved_at = Column(TIMESTAMP)
    resolved_by_user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    resolution_notes = Column(Text)
    resolution_actions = Column(JSON)  # Structured data about resolution
    
    # Notification tracking
    notified_channels = Column(JSON)  # {email: true, slack: true, webhook: true}
    notification_sent_at = Column(TIMESTAMP)
    
    # Timestamps
    created_at = Column(TIMESTAMP, server_default=func.now(), index=True)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    # TODO: Uncomment after creating ConflictEventNew model in conflict.py
    #       1. Create ConflictEventNew(Base) class matching conflict_events_new table
    #       2. Import in app/models/__init__.py
    #       3. Uncomment line below
    # conflict_event = relationship("ConflictEventNew", backref="alerts", foreign_keys=[conflict_event_id])


class AlertReadStatus(Base):
    """Track which users have read which alerts"""
    __tablename__ = "alert_read_status"
    
    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(Integer, ForeignKey('alert_events.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    read_at = Column(TIMESTAMP, server_default=func.now())
    
    __table_args__ = (
        {'schema': None},
    )
