from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.db.database import get_db
from app.models.forecast import Forecast
from app.schemas.forecast import Forecast as ForecastSchema, ForecastCreate

router = APIRouter()


@router.get("/", response_model=List[ForecastSchema])
async def get_forecasts(
    location_type: Optional[str] = Query(None, regex="^(state|lga)$"),
    location_name: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db)
):
    """Get conflict forecasts"""
    query = db.query(Forecast)
    
    if location_type:
        query = query.filter(Forecast.location_type == location_type)
    if location_name:
        query = query.filter(Forecast.location_name == location_name)
    if start_date:
        query = query.filter(Forecast.target_date >= start_date)
    if end_date:
        query = query.filter(Forecast.target_date <= end_date)
    
    forecasts = query.order_by(Forecast.target_date).all()
    return forecasts


@router.get("/{location_name}")
async def get_location_forecast(
    location_name: str,
    location_type: str = Query(..., regex="^(state|lga)$"),
    weeks_ahead: int = Query(4, ge=1, le=12),
    db: Session = Depends(get_db)
):
    """Get forecast for specific location"""
    
    start_date = datetime.now()
    end_date = start_date + timedelta(weeks=weeks_ahead)
    
    forecasts = db.query(Forecast).filter(
        Forecast.location_name == location_name,
        Forecast.location_type == location_type,
        Forecast.target_date >= start_date,
        Forecast.target_date <= end_date
    ).order_by(Forecast.target_date).all()
    
    if not forecasts:
        # Generate mock forecast if none exists
        forecasts = generate_mock_forecast(location_name, location_type, weeks_ahead)
    
    return {
        "location": location_name,
        "location_type": location_type,
        "forecasts": forecasts,
        "summary": calculate_forecast_summary(forecasts)
    }


@router.post("/", response_model=ForecastSchema)
async def create_forecast(forecast: ForecastCreate, db: Session = Depends(get_db)):
    """Create new forecast"""
    db_forecast = Forecast(**forecast.dict())
    db.add(db_forecast)
    db.commit()
    db.refresh(db_forecast)
    return db_forecast


@router.get("/risk/assessment")
async def get_risk_assessment(
    location_type: str = Query(..., regex="^(state|lga)$"),
    db: Session = Depends(get_db)
):
    """Get risk assessment for all locations of a type"""
    
    # Get the latest forecast for each location
    latest_date = datetime.now() + timedelta(weeks=4)  # 4-week ahead forecast
    
    risk_assessment = db.query(
        Forecast.location_name,
        Forecast.risk_level,
        Forecast.risk_score,
        Forecast.predicted_incidents,
        Forecast.predicted_casualties
    ).filter(
        Forecast.location_type == location_type,
        Forecast.target_date >= latest_date - timedelta(days=7),
        Forecast.target_date <= latest_date + timedelta(days=7)
    ).order_by(Forecast.risk_score.desc()).all()
    
    return [
        {
            "location": assessment.location_name,
            "risk_level": assessment.risk_level,
            "risk_score": assessment.risk_score,
            "predicted_incidents": assessment.predicted_incidents,
            "predicted_casualties": assessment.predicted_casualties
        }
        for assessment in risk_assessment
    ]


def generate_mock_forecast(location_name: str, location_type: str, weeks_ahead: int):
    """Generate mock forecast data for demonstration"""
    import random
    
    forecasts = []
    base_risk = random.uniform(0.2, 0.8)
    
    for week in range(1, weeks_ahead + 1):
        target_date = datetime.now() + timedelta(weeks=week)
        
        # Add some variation to risk
        risk_score = max(0.1, min(0.9, base_risk + random.uniform(-0.2, 0.2)))
        
        if risk_score >= 0.7:
            risk_level = "very_high"
        elif risk_score >= 0.5:
            risk_level = "high"
        elif risk_score >= 0.3:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        forecast = {
            "id": f"mock-{location_name}-{week}",
            "location_name": location_name,
            "location_type": location_type,
            "target_date": target_date,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "predicted_incidents": max(0, int(risk_score * 10 + random.uniform(-2, 2))),
            "predicted_casualties": max(0, int(risk_score * 5 + random.uniform(-1, 1))),
            "model_version": "mock-v1.0",
            "confidence_interval": {"lower": max(0.1, risk_score - 0.2), "upper": min(0.9, risk_score + 0.2)},
            "contributing_factors": ["historical_patterns", "seasonal_trends", "mock_data"]
        }
        forecasts.append(forecast)
    
    return forecasts


def calculate_forecast_summary(forecasts):
    """Calculate summary statistics for forecasts"""
    if not forecasts:
        return {}
    
    avg_risk_score = sum(f.risk_score for f in forecasts) / len(forecasts)
    total_incidents = sum(f.predicted_incidents for f in forecasts)
    total_casualties = sum(f.predicted_casualties for f in forecasts)
    
    risk_levels = [f.risk_level for f in forecasts]
    most_common_risk = max(set(risk_levels), key=risk_levels.count)
    
    return {
        "average_risk_score": avg_risk_score,
        "total_predicted_incidents": total_incidents,
        "total_predicted_casualties": total_casualties,
        "most_common_risk_level": most_common_risk,
        "forecast_weeks": len(forecasts)
    }
