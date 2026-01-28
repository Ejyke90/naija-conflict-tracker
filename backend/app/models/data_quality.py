"""Data Quality Metrics Model for tracking geocoding and validation statistics"""

from sqlalchemy import Column, Integer, Float, DateTime, String, Index
from datetime import datetime
from app.db.base_class import Base


class DataQualityMetric(Base):
    """Track geocoding and validation success rates for real-time monitoring"""
    
    __tablename__ = "data_quality_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Timestamp for the metric
    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)
    
    # Geocoding metrics
    geocoding_attempts = Column(Integer, default=0)
    geocoding_successes = Column(Integer, default=0)
    geocoding_success_rate = Column(Float, default=0.0)  # Percentage (0-100)
    
    # Validation metrics
    validation_attempts = Column(Integer, default=0)
    validation_passes = Column(Integer, default=0)
    validation_pass_rate = Column(Float, default=0.0)  # Percentage (0-100)
    
    # Classification
    metric_type = Column(String(50), default="aggregate")  # aggregate, source-specific, hourly
    source = Column(String(100), nullable=True, index=True)  # news source or pipeline stage
    
    # Status
    status = Column(String(20), default="pending")  # pending, healthy, warning, error
    
    # Metadata
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, server_default="NOW()")
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes for efficient querying
    __table_args__ = (
        Index('idx_quality_timestamp_desc', 'timestamp'),
        Index('idx_quality_source', 'source'),
        Index('idx_quality_type', 'metric_type'),
        Index('idx_quality_recent', 'timestamp', 'metric_type'),
    )
    
    def __repr__(self):
        return (
            f"<DataQualityMetric(timestamp={self.timestamp}, "
            f"geocoding_rate={self.geocoding_success_rate:.1f}%, "
            f"validation_rate={self.validation_pass_rate:.1f}%)>"
        )
