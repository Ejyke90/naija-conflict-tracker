from sqlalchemy import Boolean, Column, Date, DateTime, Float, Integer, String, Text
from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.base_class import Base


class ConflictEvent(Base):
    """Legacy conflict_events table (source data before migration)"""
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
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Conflict(Base):
    """New normalized conflicts table"""
    __tablename__ = "conflicts"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    # Date and classification
    incidence_date = Column(Date, nullable=False, index=True)
    conflict_type_id = Column(BigInteger, ForeignKey("conflict_types.id"), index=True)

    # Location hierarchy
    country_id = Column(BigInteger, ForeignKey("countries.id"), index=True)
    region_id = Column(BigInteger, ForeignKey("regions.id"), index=True)
    state_id = Column(BigInteger, ForeignKey("states.id"), index=True)
    lga_id = Column(BigInteger, ForeignKey("lgas.id"), index=True)
    community = Column(String(255))

    # Casualties (gender-disaggregated)
    civilian_death_male = Column(Integer, default=0)
    civilian_death_female = Column(Integer, default=0)
    civilian_death_unknown = Column(Integer, default=0)
    security_death_male = Column(Integer, default=0)
    security_death_female = Column(Integer, default=0)
    security_death_unknown = Column(Integer, default=0)
    injured_male = Column(Integer, default=0)
    injured_female = Column(Integer, default=0)
    injured_unknown = Column(Integer, default=0)
    kidnapped_male = Column(Integer, default=0)
    kidnapped_female = Column(Integer, default=0)
    kidnapped_unknown = Column(Integer, default=0)

    # Displacement
    displaced_persons = Column(String(10))
    displaced_male = Column(Integer, default=0)
    displaced_female = Column(Integer, default=0)

    # Actors
    actor_1 = Column(BigInteger, ForeignKey("actors.id"), index=True)
    actor_2 = Column(BigInteger, ForeignKey("actors.id"), index=True)
    actor_3 = Column(BigInteger, ForeignKey("actors.id"), index=True)

    # Details and metadata
    description = Column(Text)
    action = Column(Text)
    highway_roads_water = Column(Text)
    confirmation_verification = Column(String(255))
    verification_level = Column(String(255))
    source_url = Column(Text)
    source_contact_details = Column(Text)
    source_contact_pictures = Column(String(255))
    source_metadata = Column(Text)
    data_source = Column(String(255))

    reporter_id = Column(BigInteger)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True))

    # Relationships for eager loading
    conflict_type_rel = relationship("ConflictType", foreign_keys=[conflict_type_id])
    region_rel = relationship("Region", foreign_keys=[region_id])
    state_rel = relationship("State", foreign_keys=[state_id])
    lga_rel = relationship("LGA", foreign_keys=[lga_id])
    actor_1_rel = relationship("Actor", foreign_keys=[actor_1])
    actor_2_rel = relationship("Actor", foreign_keys=[actor_2])
    actor_3_rel = relationship("Actor", foreign_keys=[actor_3])
