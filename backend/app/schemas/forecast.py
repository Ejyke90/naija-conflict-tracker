from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID


class ForecastBase(BaseModel):
    forecast_date: datetime
    target_date: datetime
    location_type: str = Field(..., regex="^(state|lga)$")
    location_name: str
    risk_score: Optional[float] = Field(None, ge=0, le=1)
    risk_level: Optional[str] = Field(None, regex="^(low|medium|high|very_high)$")
    predicted_incidents: Optional[int] = Field(None, ge=0)
    predicted_casualties: Optional[int] = Field(None, ge=0)
    model_version: Optional[str] = None
    confidence_interval: Optional[Dict[str, float]] = None
    contributing_factors: Optional[Dict[str, Any]] = None


class ForecastCreate(ForecastBase):
    pass


class Forecast(ForecastBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
