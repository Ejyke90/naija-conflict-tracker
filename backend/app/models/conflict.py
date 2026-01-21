from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Date
from app.db.base_class import Base


class Conflict(Base):
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
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
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
