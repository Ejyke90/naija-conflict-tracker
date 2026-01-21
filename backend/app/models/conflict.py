from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base_class import Base
import uuid


class Conflict(Base):
    __tablename__ = "conflicts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Event details
    event_date = Column(DateTime, nullable=False, index=True)
    conflict_type = Column(String(100), index=True)  # Matches actual database column
    archetype = Column(String(100), index=True)
    description = Column(Text)
    
    # Location (hierarchical)
    state = Column(String(50), nullable=False, index=True)
    lga = Column(String(100), index=True)
    community = Column(String(200), index=True)
    location_detail = Column(Text)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # Casualties (gender-disaggregated)
    fatalities_male = Column(Integer, default=0)
    fatalities_female = Column(Integer, default=0)
    fatalities_unknown = Column(Integer, default=0)
    injured_male = Column(Integer, default=0)
    injured_female = Column(Integer, default=0)
    injured_unknown = Column(Integer, default=0)
    kidnapped_male = Column(Integer, default=0)
    kidnapped_female = Column(Integer, default=0)
    kidnapped_unknown = Column(Integer, default=0)
    displaced = Column(Integer, default=0)
    
    # Actors
    perpetrator_group = Column(String(200), index=True)
    target_group = Column(String(200))
    # actor_id = Column(Integer, ForeignKey('actors.id'))  # Temporarily disabled
    # Removed actor relationship to troubleshoot mapper error
    # actor = relationship("Actor", backref="conflicts")
    
    # Data provenance
    source_type = Column(String(50), index=True)  # news, social_media, official, manual
    source_url = Column(Text)
    source_reliability = Column(Integer)  # 1-5 scale
    confidence_score = Column(Float)  # 0-1 scale
    
    # Metadata
    verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default="now()")
    updated_at = Column(DateTime, default="now()")
