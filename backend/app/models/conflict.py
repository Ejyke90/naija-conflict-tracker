from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Date, Boolean
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.base_class import Base


class ConflictEvent(Base):
    """Supabase conflict_events table model"""
    __tablename__ = "conflict_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Event details
    event_date = Column(Date, nullable=False, index=True)
    year = Column(Integer, nullable=False, index=True)
    month = Column(Integer, nullable=False, index=True)
    
    # Event Classification
    event_type = Column(String(100), nullable=False, index=True)
    event_category = Column(String(100))
    conflict_type = Column(String(100))
    
    # Location
    state = Column(String(50), nullable=False, index=True)
    lga = Column(String(100), index=True)
    location = Column(String(255))
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Actors
    actor1 = Column(String(255))
    actor2 = Column(String(255))
    actor1_type = Column(String(100))
    actor2_type = Column(String(100))
    
    # Impact
    fatalities = Column(Integer, default=0)
    injuries = Column(Integer, default=0)
    properties_destroyed = Column(Integer, default=0)
    displaced_persons = Column(Integer, default=0)
    
    # Metadata
    source = Column(Text)
    notes = Column(Text)
    verified = Column(Boolean, default=False)
    confidence_level = Column(String(20))  # 'High', 'Medium', 'Low'
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default="NOW()")
    updated_at = Column(DateTime(timezone=True), server_default="NOW()", onupdate="NOW()")


# Keep old model for backwards compatibility during migration
class Conflict(Base):
    """Legacy conflicts table model (Railway)"""
    __tablename__ = "conflicts"

    id = Column(Integer, primary_key=True)
    
    # Event details
    event_date = Column(Date, nullable=False, index=True)
    conflict_type = Column(String(100), index=True)
    description = Column(Text)
    
    # Location (hierarchical)
    state = Column(String(100), index=True)
    lga = Column(String(100), index=True)
    community = Column(String(255))
    
    # Actors
    actor1 = Column(String(255))
    actor2 = Column(String(255))
    actor3 = Column(String(255))
    
    # Casualties (from Excel import)
    fatalities = Column(Integer, default=0)
    civilian_casualties = Column(Integer, default=0)
    gsa_casualties = Column(Integer, default=0)
    injured = Column(Integer, default=0)
    kidnapped = Column(Integer, default=0)
    displaced = Column(Integer, default=0)
    
    # Data provenance
    source = Column(String(255))
    source_url = Column(Text)
    data_source = Column(String(100))
    
    # Metadata
    created_at = Column(DateTime, default="now()")
