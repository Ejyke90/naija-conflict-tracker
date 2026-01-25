from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime, date
from typing import Optional, List
from uuid import UUID


class ConflictEventBase(BaseModel):
    """Base schema for conflict events (Supabase)"""
    event_date: date
    year: int = Field(..., ge=1990, le=2100)
    month: int = Field(..., ge=1, le=12)
    
    # Event Classification
    event_type: str
    event_category: Optional[str] = None
    conflict_type: Optional[str] = None
    
    # Location
    state: str
    lga: Optional[str] = None
    location: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    
    # Actors
    actor1: Optional[str] = None
    actor2: Optional[str] = None
    actor1_type: Optional[str] = None
    actor2_type: Optional[str] = None
    
    # Impact
    fatalities: int = Field(0, ge=0)
    injuries: int = Field(0, ge=0)
    properties_destroyed: int = Field(0, ge=0)
    displaced_persons: int = Field(0, ge=0)
    
    # Metadata
    source: Optional[str] = None
    notes: Optional[str] = None
    verified: bool = False
    confidence_level: Optional[str] = Field(None, pattern="^(High|Medium|Low)$")


class ConflictEventCreate(ConflictEventBase):
    """Schema for creating new conflict events"""
    pass


class ConflictEventUpdate(BaseModel):
    """Schema for updating conflict events"""
    event_type: Optional[str] = None
    event_category: Optional[str] = None
    conflict_type: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    fatalities: Optional[int] = Field(None, ge=0)
    injuries: Optional[int] = Field(None, ge=0)
    properties_destroyed: Optional[int] = Field(None, ge=0)
    displaced_persons: Optional[int] = Field(None, ge=0)
    actor1: Optional[str] = None
    actor2: Optional[str] = None
    verified: Optional[bool] = None
    confidence_level: Optional[str] = Field(None, pattern="^(High|Medium|Low)$")
    notes: Optional[str] = None


class ConflictEvent(ConflictEventBase):
    """Schema for returning conflict events"""
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Legacy schemas for backwards compatibility
class ConflictBase(BaseModel):
    event_date: date
    event_type: str
    archetype: Optional[str] = None
    description: Optional[str] = None
    state: str
    lga: Optional[str] = None
    community: Optional[str] = None
    location_detail: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    fatalities_male: int = 0
    fatalities_female: int = 0
    fatalities_unknown: int = 0
    injured_male: int = 0
    injured_female: int = 0
    injured_unknown: int = 0
    kidnapped_male: int = 0
    kidnapped_female: int = 0
    kidnapped_unknown: int = 0
    displaced: int = 0
    perpetrator_group: Optional[str] = None
    target_group: Optional[str] = None
    source_type: Optional[str] = None
    source_url: Optional[str] = None
    source_reliability: Optional[int] = Field(None, ge=1, le=5)
    confidence_score: Optional[float] = Field(None, ge=0, le=1)
    verified: bool = False


class ConflictCreate(ConflictBase):
    pass


class ConflictUpdate(BaseModel):
    event_type: Optional[str] = None
    archetype: Optional[str] = None
    description: Optional[str] = None
    fatalities_male: Optional[int] = None
    fatalities_female: Optional[int] = None
    fatalities_unknown: Optional[int] = None
    injured_male: Optional[int] = None
    injured_female: Optional[int] = None
    injured_unknown: Optional[int] = None
    kidnapped_male: Optional[int] = None
    kidnapped_female: Optional[int] = None
    kidnapped_unknown: Optional[int] = None
    displaced: Optional[int] = None
    perpetrator_group: Optional[str] = None
    target_group: Optional[str] = None
    verified: Optional[bool] = None


class Conflict(ConflictBase):
    id: UUID
    coordinates: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConflictSummary(BaseModel):
    total_incidents: int
    total_fatalities: int
    total_injured: int
    total_displaced: int
    states_affected: int
    lgas_affected: int


class ConflictStats(BaseModel):
    by_state: List[dict]
    by_event_type: List[dict]
    by_month: List[dict]
    gender_impact: dict
