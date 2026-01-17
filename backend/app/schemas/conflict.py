from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from uuid import UUID


class ConflictBase(BaseModel):
    event_date: datetime
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

    class Config:
        from_attributes = True


class ConflictSummary(BaseModel):
    total_incidents: int
    total_fatalities: int
    total_injured: int
    total_kidnapped: int
    total_displaced: int
    states_affected: int
    lgas_affected: int


class ConflictStats(BaseModel):
    by_state: List[dict]
    by_event_type: List[dict]
    by_month: List[dict]
    gender_impact: dict
