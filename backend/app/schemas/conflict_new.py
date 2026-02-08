"""
Pydantic schemas for the new normalized conflicts schema.
These schemas work with the new Conflict model (not legacy ConflictEvent).
"""
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


# Actor schemas
class ActorBase(BaseModel):
    title: str = Field(..., max_length=255)

class Actor(ActorBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Conflict Type schemas
class ConflictTypeBase(BaseModel):
    title: str = Field(..., max_length=255)

class ConflictType(ConflictTypeBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Region schemas
class RegionBase(BaseModel):
    name: str = Field(..., max_length=255)

class Region(RegionBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# State schemas
class StateBase(BaseModel):
    name: str = Field(..., max_length=255)
    region_id: Optional[int] = None

class State(StateBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# LGA schemas
class LGABase(BaseModel):
    name: str = Field(..., max_length=255)
    state_id: Optional[int] = None

class LGA(LGABase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Main Conflict schemas
class ConflictBase(BaseModel):
    """Base conflict data (for create/update operations)"""
    incidence_date: date
    conflict_type_id: Optional[int] = None
    
    # Location
    country_id: Optional[int] = 1  # Default: Nigeria
    region_id: Optional[int] = None
    state_id: Optional[int] = None
    lga_id: Optional[int] = None
    community: Optional[str] = Field(None, max_length=255)
    
    # Casualties (gender-disaggregated)
    civilian_death_male: int = 0
    civilian_death_female: int = 0
    civilian_death_unknown: int = 0
    security_death_male: int = 0
    security_death_female: int = 0
    security_death_unknown: int = 0
    injured_male: int = 0
    injured_female: int = 0
    injured_unknown: int = 0
    kidnapped_male: int = 0
    kidnapped_female: int = 0
    kidnapped_unknown: int = 0
    
    # Displacement
    displaced_persons: Optional[str] = Field(None, max_length=10)
    displaced_male: int = 0
    displaced_female: int = 0
    
    # Actors
    actor_1: Optional[int] = None
    actor_2: Optional[int] = None
    actor_3: Optional[int] = None
    
    # Details
    description: Optional[str] = None
    action: Optional[str] = None
    highway_roads_water: Optional[str] = None
    
    # Verification
    confirmation_verification: Optional[str] = Field(None, max_length=255)
    verification_level: Optional[str] = Field(None, max_length=255)
    source_url: Optional[str] = None
    source_contact_details: Optional[str] = None
    source_contact_pictures: Optional[str] = Field(None, max_length=255)
    source_metadata: Optional[str] = None
    data_source: Optional[str] = Field(None, max_length=255)
    
    reporter_id: Optional[int] = None


class ConflictCreate(ConflictBase):
    """Schema for creating new conflict record"""
    pass


class ConflictUpdate(BaseModel):
    """Schema for updating conflict record (all fields optional)"""
    incidence_date: Optional[date] = None
    conflict_type_id: Optional[int] = None
    state_id: Optional[int] = None
    lga_id: Optional[int] = None
    community: Optional[str] = None
    
    civilian_death_male: Optional[int] = None
    civilian_death_female: Optional[int] = None
    civilian_death_unknown: Optional[int] = None
    security_death_male: Optional[int] = None
    security_death_female: Optional[int] = None
    security_death_unknown: Optional[int] = None
    injured_male: Optional[int] = None
    injured_female: Optional[int] = None
    injured_unknown: Optional[int] = None
    
    actor_1: Optional[int] = None
    actor_2: Optional[int] = None
    actor_3: Optional[int] = None
    
    description: Optional[str] = None
    verification_level: Optional[str] = None
    source_url: Optional[str] = None


class Conflict(ConflictBase):
    """Full conflict record (from database)"""
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ConflictWithDetails(Conflict):
    """Conflict with joined reference data (actors, types, locations)"""
    conflict_type: Optional[ConflictType] = None
    region: Optional[Region] = None
    state: Optional[State] = None
    lga: Optional[LGA] = None
    actor_1_obj: Optional[Actor] = None
    actor_2_obj: Optional[Actor] = None
    actor_3_obj: Optional[Actor] = None
    
    # Computed totals
    total_deaths: int = 0
    total_civilian_deaths: int = 0
    total_security_deaths: int = 0
    total_injured: int = 0
    total_kidnapped: int = 0
    total_displaced: int = 0


class ConflictStats(BaseModel):
    """Aggregate statistics"""
    total_conflicts: int
    total_deaths: int
    total_injured: int
    total_kidnapped: int
    total_displaced: int
    date_range_start: Optional[date] = None
    date_range_end: Optional[date] = None
    by_state: Optional[dict] = None
    by_conflict_type: Optional[dict] = None
    by_month: Optional[dict] = None


class ConflictSummary(BaseModel):
    """Lightweight summary for lists/maps"""
    id: int
    incidence_date: date
    state_id: Optional[int] = None
    state_name: Optional[str] = None
    lga_name: Optional[str] = None
    community: Optional[str] = None
    conflict_type_name: Optional[str] = None
    total_deaths: int
    total_injured: int
    verification_level: Optional[str] = None
    
    class Config:
        from_attributes = True
