from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from app.db.database import get_db
from app.models.forecast import Forecast
from app.schemas.forecast import Forecast as ForecastSchema, ForecastCreate
from app.ml import ProphetForecaster, ARIMAForecaster, EnsembleForecaster, ModelEvaluator
from app.core.cache import cache_forecast, invalidate_forecast_cache, get_cache_stats

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=List[ForecastSchema])
async def get_forecasts(
    location_type: Optional[str] = Query(None, pattern="^(state|lga)$"),
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
    location_type: str = Query(..., pattern="^(state|lga)$"),
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


@cache_forecast(ttl=3600, key_prefix="advanced_forecast")  # Cache for 1 hour
@router.get("/advanced/{location_name}")
async def get_advanced_forecast(
    location_name: str,
    location_type: str = Query(..., pattern="^(state|lga)$"),
    model: str = Query("prophet", pattern="^(prophet|arima|ensemble)$"),
    weeks_ahead: int = Query(4, ge=1, le=12),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Advanced forecasting using Prophet, ARIMA, or Ensemble models
    
    Args:
        location_name: State or LGA name
        location_type: "state" or "lga"
        model: Forecasting model to use ("prophet", "arima", "ensemble")
        weeks_ahead: Number of weeks to forecast (1-12)
        
    Returns:
        Forecast with predictions, confidence intervals, and model metadata
    """
    try:
        # Select and initialize model
        if model == "prophet":
            forecaster = ProphetForecaster()
            result = forecaster.forecast(
                state=location_name if location_type == "state" else None,
                lga=location_name if location_type == "lga" else None,
                weeks_ahead=weeks_ahead
            )
        elif model == "arima":
            forecaster = ARIMAForecaster()
            result = forecaster.forecast(
                state=location_name if location_type == "state" else None,
                lga=location_name if location_type == "lga" else None,
                weeks_ahead=weeks_ahead
            )
        elif model == "ensemble":
            forecaster = EnsembleForecaster()
            result = forecaster.forecast(
                state=location_name if location_type == "state" else None,
                lga=location_name if location_type == "lga" else None,
                weeks_ahead=weeks_ahead,
                include_individual_models=True
            )
        else:
            raise HTTPException(status_code=400, detail=f"Invalid model: {model}")
        
        if "error" in result:
            logger.warning(f"Forecast error for {location_name}: {result['error']}")
            return {
                "location": location_name,
                "location_type": location_type,
                "model": model,
                "error": result["error"],
                "forecast": []
            }
        
        return {
            "location": location_name,
            "location_type": location_type,
            "model": model,
            **result
        }
        
    except Exception as e:
        logger.error(f"Advanced forecast failed: {e}")
        raise HTTPException(status_code=500, detail=f"Forecasting error: {str(e)}")


@router.get("/compare-models/{location_name}")
async def compare_forecasting_models(
    location_name: str,
    location_type: str = Query(..., pattern="^(state|lga)$"),
    weeks_ahead: int = Query(4, ge=1, le=12)
) -> Dict[str, Any]:
    """
    Compare Prophet, ARIMA, and Ensemble models side-by-side
    
    Useful for model selection and understanding prediction variance
    """
    try:
        results = {}
        
        # Run all three models
        for model_name in ["prophet", "arima", "ensemble"]:
            try:
                if model_name == "prophet":
                    forecaster = ProphetForecaster()
                    result = forecaster.forecast(
                        state=location_name if location_type == "state" else None,
                        lga=location_name if location_type == "lga" else None,
                        weeks_ahead=weeks_ahead
                    )
                elif model_name == "arima":
                    forecaster = ARIMAForecaster()
                    result = forecaster.forecast(
                        state=location_name if location_type == "state" else None,
                        lga=location_name if location_type == "lga" else None,
                        weeks_ahead=weeks_ahead
                    )
                else:  # ensemble
                    forecaster = EnsembleForecaster()
                    result = forecaster.forecast(
                        state=location_name if location_type == "state" else None,
                        lga=location_name if location_type == "lga" else None,
                        weeks_ahead=weeks_ahead
                    )
                
                results[model_name] = result
                
            except Exception as e:
                logger.error(f"{model_name} forecast failed: {e}")
                results[model_name] = {"error": str(e)}
        
        return {
            "location": location_name,
            "location_type": location_type,
            "weeks_ahead": weeks_ahead,
            "models": results,
            "recommendation": _recommend_best_model(results)
        }
        
    except Exception as e:
        logger.error(f"Model comparison failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models/evaluation")
async def evaluate_model_performance(
    state: Optional[str] = Query(None, description="State to evaluate"),
    lga: Optional[str] = Query(None, description="LGA to evaluate"),
    test_size: int = Query(12, ge=4, le=24, description="Test weeks for backtesting")
) -> Dict[str, Any]:
    """
    Evaluate and compare model performance using backtesting
    
    Returns:
    - MAE (Mean Absolute Error)
    - RMSE (Root Mean Squared Error)
    - MAPE (Mean Absolute Percentage Error)
    - Coverage (% within confidence interval)
    - Direction Accuracy
    """
    try:
        evaluator = ModelEvaluator()
        
        results = evaluator.compare_models(
            state=state,
            lga=lga,
            test_size=test_size
        )
        
        if "error" in results:
            return {
                "error": results["error"],
                "evaluation": {}
            }
        
        # Add performance ratings
        for model_name, model_result in results["comparison"].items():
            if "metrics" in model_result:
                model_result["performance_rating"] = evaluator.get_performance_summary(
                    model_result["metrics"]
                )
        
        return {
            "location": {"state": state, "lga": lga},
            "test_size_weeks": test_size,
            "evaluation": results,
            "recommendation": f"Use {results['best_model']} (MAE: {results['best_mae']})"
        }
        
    except Exception as e:
        logger.error(f"Model evaluation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/risk/assessment")
async def get_risk_assessment(
    location_type: str = Query(..., pattern="^(state|lga)$"),
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


def _recommend_best_model(results: Dict[str, Any]) -> str:
    """
    Recommend best model based on available forecasts
    
    Priority: Ensemble > Prophet > ARIMA > None
    """
    successful_models = [
        model for model, result in results.items()
        if "error" not in result and result.get("forecast")
    ]
    
    if not successful_models:
        return "No models succeeded"
    
    if "ensemble" in successful_models:
        return "Ensemble (combines multiple models for robust predictions)"
    elif "prophet" in successful_models:
        return "Prophet (good for seasonality detection)"
    elif "arima" in successful_models:
        return "ARIMA (statistical forecasting)"
    else:
        return "Unknown"
