"""
AI Predictions Endpoint
Returns next 30-day conflict predictions for top 5 at-risk states
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging

from app.db.database import get_db
from app.models.conflict import ConflictEvent
from app.ml import EnsembleForecaster
from app.core.cache import get_redis_client

logger = logging.getLogger(__name__)
router = APIRouter()


class RiskScorer:
    """Calculate conflict risk scores for states"""
    
    @staticmethod
    def calculate_risk_score(
        incident_count: int,
        fatality_count: int,
        days: int = 30,
        severity_weight: float = 1.0,
        fatality_weight: float = 0.3
    ) -> float:
        """
        Calculate composite risk score for a state
        
        Args:
            incident_count: Number of incidents
            fatality_count: Total fatalities
            days: Number of days in period
            severity_weight: Weight for incident severity
            fatality_weight: Weight for fatalities (0-1 scale)
            
        Returns:
            Risk score (0-10 scale)
        """
        # Incidents per day
        incident_rate = incident_count / days if days > 0 else 0
        
        # Fatalities contribution
        fatalities_per_incident = fatality_count / incident_count if incident_count > 0 else 0
        fatality_score = min(fatalities_per_incident / 10, 1.0) * fatality_weight  # Normalized 0-1
        
        # Composite score: weighted sum
        # Base: incidents_per_day * 2 (scale to 0-10)
        # Adjusted: add fatality contribution
        risk_score = min(incident_rate * 2 + fatality_score * 2, 10.0)
        
        return round(risk_score, 2)
    
    @staticmethod
    def classify_risk_level(risk_score: float) -> str:
        """Classify risk level from score"""
        if risk_score >= 6:
            return "CRITICAL"
        elif risk_score >= 4:
            return "HIGH"
        elif risk_score >= 2:
            return "MEDIUM"
        else:
            return "LOW"


def get_top_at_risk_states(
    db: Session,
    days_back: int = 30,
    top_n: int = 5
) -> List[Dict[str, Any]]:
    """
    Query database for top N at-risk states
    
    Args:
        db: Database session
        days_back: Number of days to analyze (ignored if insufficient recent data)
        top_n: Number of top states to return
        
    Returns:
        List of states with risk scores, sorted by risk descending
    """
    cutoff_date = datetime.now().date() - timedelta(days=days_back)
    
    # Try to query conflicts in the recent period first
    conflicts = db.query(ConflictEvent).filter(
        ConflictEvent.event_date >= cutoff_date,
        ConflictEvent.state.isnot(None)
    ).all()
    
    # If no recent data, use all available data
    if not conflicts:
        conflicts = db.query(ConflictEvent).filter(
            ConflictEvent.state.isnot(None)
        ).all()
    
    if not conflicts:
        logger.warning(f"No conflicts found in last {days_back} days")
        return []
    
    # Aggregate by state
    state_stats = {}
    for conflict in conflicts:
        state = conflict.state
        if state not in state_stats:
            state_stats[state] = {
                "incident_count": 0,
                "fatality_count": 0,
                "state": state
            }
        
        state_stats[state]["incident_count"] += 1
        state_stats[state]["fatality_count"] += (conflict.fatalities or 0)
    
    # Calculate risk scores
    states_with_scores = []
    for state, stats in state_stats.items():
        risk_score = RiskScorer.calculate_risk_score(
            stats["incident_count"],
            stats["fatality_count"],
            days=days_back
        )
        risk_level = RiskScorer.classify_risk_level(risk_score)
        
        states_with_scores.append({
            "state": state,
            "incident_count": stats["incident_count"],
            "fatality_count": stats["fatality_count"],
            "risk_score": risk_score,
            "risk_level": risk_level
        })
    
    # Sort by risk score descending and get top N
    states_with_scores.sort(key=lambda x: x["risk_score"], reverse=True)
    return states_with_scores[:top_n]


def generate_predictions_for_state(
    state: str,
    forecaster: EnsembleForecaster
) -> Dict[str, Any]:
    """
    Generate 30-day predictions for a single state
    
    Args:
        state: State name
        forecaster: EnsembleForecaster instance
        
    Returns:
        Dictionary with predictions, CI, and metadata
    """
    try:
        # Generate 4-week forecast
        result = forecaster.forecast(
            state=state,
            weeks_ahead=4,
            include_individual_models=False
        )
        
        if "error" in result:
            logger.warning(f"Forecast error for {state}: {result['error']}")
            return {
                "state": state,
                "error": result["error"]
            }
        
        forecast_data = result.get("forecast", [])
        
        # Aggregate to 30-day totals
        predicted_incidents = sum(
            item.get("predicted_incidents", 0) for item in forecast_data
        )
        predicted_fatalities = sum(
            item.get("predicted_fatalities", 0) for item in forecast_data
        )
        
        # Confidence intervals (lower and upper bounds)
        incidents_lower = sum(
            item.get("lower_bound_incidents", item.get("lower_bound", 0)) 
            for item in forecast_data
        )
        incidents_upper = sum(
            item.get("upper_bound_incidents", item.get("upper_bound", 0)) 
            for item in forecast_data
        )
        
        fatalities_lower = sum(
            item.get("lower_bound_fatalities", 0) for item in forecast_data
        )
        fatalities_upper = sum(
            item.get("upper_bound_fatalities", 0) for item in forecast_data
        )
        
        # Get MAPE (Mean Absolute Percentage Error) from result metadata
        mape = result.get("metadata", {}).get("mape", None)
        if mape:
            # Convert to accuracy percentage (e.g., MAPE 0.18 = 82% accuracy)
            accuracy = round((1 - min(mape, 1)) * 100, 0)
        else:
            accuracy = None
        
        model_type = result.get("metadata", {}).get("model_type", "ensemble")
        last_trained = result.get("metadata", {}).get("last_trained", None)
        
        return {
            "state": state,
            "next_30_days": {
                "predicted_incidents": round(predicted_incidents, 1),
                "incidents_ci_lower": round(incidents_lower, 1),
                "incidents_ci_upper": round(incidents_upper, 1),
                "predicted_fatalities": round(predicted_fatalities, 1),
                "fatalities_ci_lower": round(fatalities_lower, 1),
                "fatalities_ci_upper": round(fatalities_upper, 1)
            },
            "model": model_type,
            "mape": round(mape, 3) if mape else None,
            "accuracy_percent": accuracy,
            "last_trained": last_trained
        }
        
    except Exception as e:
        logger.error(f"Error generating predictions for {state}: {e}")
        return {
            "state": state,
            "error": str(e)
        }


@router.get("/next-30-days")
async def get_predictions_next_30_days(
    db: Session = Depends(get_db),
    top_states: int = Query(5, ge=1, le=10)
):
    """
    Get AI-powered conflict predictions for next 30 days
    
    Returns predictions for the top N most at-risk states including:
    - Predicted incidents and fatalities
    - 90% confidence intervals
    - Model accuracy metrics
    
    **Requires:** No authentication (public endpoint for MVP)
    
    **Parameters:**
    - `top_states`: Number of top at-risk states to return (1-10, default 5)
    
    **Returns:**
    - List of predictions with confidence intervals and accuracy metrics
    """
    try:
        # Get top at-risk states
        top_risk_states = get_top_at_risk_states(db, days_back=30, top_n=top_states)
        
        if not top_risk_states:
            return {
                "timestamp": datetime.now().isoformat(),
                "predictions": [],
                "metadata": {
                    "message": "No conflict data available for predictions",
                    "total_states_analyzed": 0
                }
            }
        
        # Generate forecaster
        forecaster = EnsembleForecaster()
        
        # Generate predictions for each top state
        predictions = []
        for rank, state_info in enumerate(top_risk_states, 1):
            state = state_info["state"]
            
            # Generate predictions
            pred_result = generate_predictions_for_state(state, forecaster)
            
            if "error" not in pred_result:
                # Add rank and current risk info
                pred_result["rank"] = rank
                pred_result["risk_level"] = state_info["risk_level"]
                pred_result["risk_score"] = state_info["risk_score"]
                predictions.append(pred_result)
            else:
                logger.warning(f"Skipping {state} due to: {pred_result['error']}")
        
        return {
            "timestamp": datetime.now().isoformat(),
            "predictions": predictions,
            "metadata": {
                "total_states_analyzed": len(top_risk_states),
                "top_states_returned": len(predictions),
                "analysis_period_days": 30,
                "forecast_horizon_days": 30,
                "refresh_interval_hours": 6,
                "accuracy_note": "MAPE = Mean Absolute Percentage Error (lower is better, accuracy = 100% - MAPE)"
            }
        }
        
    except Exception as e:
        logger.error(f"Error in predictions endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
