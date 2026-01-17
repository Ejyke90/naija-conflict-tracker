from sqlalchemy import Column, String, Integer, Float, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.db.base_class import Base
import uuid


class Forecast(Base):
    __tablename__ = "forecasts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    forecast_date = Column(DateTime, nullable=False, index=True)
    target_date = Column(DateTime, nullable=False, index=True)
    location_type = Column(String(20), index=True)  # state, lga
    location_name = Column(String(200), index=True)
    
    # Predictions
    risk_score = Column(Float)  # 0-1 scale
    risk_level = Column(String(20), index=True)  # low, medium, high, very_high
    predicted_incidents = Column(Integer)
    predicted_casualties = Column(Integer)
    
    # Model metadata
    model_version = Column(String(50))
    confidence_interval = Column(JSONB)  # {lower: 0.3, upper: 0.7}
    contributing_factors = Column(JSONB)
    
    created_at = Column(DateTime, default="now()")
