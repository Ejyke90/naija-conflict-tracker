"""
Celery Tasks for Scheduled Forecast Generation
Automatically generates forecasts for all states daily
"""

from celery import Celery
from celery.schedules import crontab
import logging
from datetime import datetime
from typing import List, Dict, Any

from app.ml import ProphetForecaster, EnsembleForecaster
from app.db.database import SessionLocal
from app.models.forecast import Forecast as ForecastModel
from sqlalchemy import text

logger = logging.getLogger(__name__)

# Initialize Celery
celery_app = Celery(
    "forecast_tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Africa/Lagos",
    enable_utc=True,
    beat_schedule={
        "generate-daily-forecasts": {
            "task": "app.tasks.forecast_tasks.generate_all_state_forecasts",
            "schedule": crontab(hour=2, minute=0),  # 2 AM daily
        },
        "generate-weekly-reports": {
            "task": "app.tasks.forecast_tasks.generate_weekly_forecast_report",
            "schedule": crontab(day_of_week=1, hour=6, minute=0),  # Monday 6 AM
        },
    },
)


@celery_app.task(bind=True, max_retries=3)
def generate_state_forecast(self, state: str, model: str = "ensemble") -> Dict[str, Any]:
    """
    Generate forecast for a single state
    
    Args:
        state: State name
        model: Model to use (prophet, arima, ensemble)
        
    Returns:
        Dictionary with forecast results
    """
    try:
        logger.info(f"Generating {model} forecast for {state}")
        
        # Select forecaster
        if model == "prophet":
            forecaster = ProphetForecaster()
        elif model == "ensemble":
            forecaster = EnsembleForecaster()
        else:
            raise ValueError(f"Unknown model: {model}")
        
        # Generate forecast
        result = forecaster.forecast(
            state=state,
            weeks_ahead=4
        )
        
        if "error" in result:
            logger.warning(f"Forecast failed for {state}: {result['error']}")
            return {"state": state, "status": "failed", "error": result["error"]}
        
        # Save to database
        db = SessionLocal()
        try:
            saved_count = _save_forecasts_to_db(db, state, result)
            db.commit()
            logger.info(f"Saved {saved_count} forecasts for {state}")
        finally:
            db.close()
        
        return {
            "state": state,
            "status": "success",
            "forecasts_saved": saved_count,
            "model": model
        }
        
    except Exception as e:
        logger.error(f"Error generating forecast for {state}: {e}")
        self.retry(exc=e, countdown=300)  # Retry after 5 minutes


@celery_app.task
def generate_all_state_forecasts(model: str = "ensemble") -> Dict[str, Any]:
    """
    Generate forecasts for all Nigerian states
    Runs daily via Celery Beat
    """
    logger.info("Starting daily forecast generation for all states")
    
    # Get list of all states with sufficient data
    db = SessionLocal()
    try:
        query = text("""
            SELECT DISTINCT state
            FROM conflicts
            WHERE state IS NOT NULL
              AND event_date >= CURRENT_DATE - INTERVAL '6 months'
            GROUP BY state
            HAVING COUNT(*) >= 10
            ORDER BY state
        """)
        
        result = db.execute(query)
        states = [row[0] for row in result]
        
        logger.info(f"Found {len(states)} states with sufficient data")
        
    finally:
        db.close()
    
    # Generate forecasts for each state
    results = []
    for state in states:
        try:
            result = generate_state_forecast.delay(state, model)
            results.append({
                "state": state,
                "task_id": result.id,
                "status": "queued"
            })
        except Exception as e:
            logger.error(f"Failed to queue forecast for {state}: {e}")
            results.append({
                "state": state,
                "status": "queue_failed",
                "error": str(e)
            })
    
    return {
        "timestamp": datetime.now().isoformat(),
        "total_states": len(states),
        "queued": len([r for r in results if r["status"] == "queued"]),
        "failed": len([r for r in results if r["status"] == "queue_failed"]),
        "results": results
    }


@celery_app.task
def generate_weekly_forecast_report() -> Dict[str, Any]:
    """
    Generate weekly PDF report with forecasts
    Runs every Monday at 6 AM
    """
    from app.reports.forecast_report import generate_forecast_pdf_report
    
    logger.info("Generating weekly forecast report")
    
    try:
        report_path = generate_forecast_pdf_report(
            weeks_ahead=4,
            include_charts=True
        )
        
        # TODO: Email report to stakeholders
        logger.info(f"Weekly report generated: {report_path}")
        
        return {
            "status": "success",
            "report_path": report_path,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Weekly report generation failed: {e}")
        return {
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


def _save_forecasts_to_db(db, state: str, forecast_result: Dict[str, Any]) -> int:
    """Save forecast results to database"""
    saved_count = 0
    
    for pred in forecast_result.get("forecast", []):
        try:
            # Calculate risk level based on prediction
            incidents = pred.get("predicted_incidents", 0)
            if incidents >= 15:
                risk_level = "very_high"
                risk_score = 0.9
            elif incidents >= 10:
                risk_level = "high"
                risk_score = 0.7
            elif incidents >= 5:
                risk_level = "medium"
                risk_score = 0.5
            else:
                risk_level = "low"
                risk_score = 0.3
            
            # Create forecast record
            forecast = ForecastModel(
                forecast_date=datetime.now(),
                target_date=datetime.fromisoformat(pred["date"]),
                location_type="state",
                location_name=state,
                risk_score=risk_score,
                risk_level=risk_level,
                predicted_incidents=int(pred.get("predicted_incidents", 0)),
                predicted_casualties=int(pred.get("predicted_incidents", 0) * 2.5),  # Estimate
                model_version=forecast_result.get("metadata", {}).get("model", "unknown"),
                confidence_interval={
                    "lower": pred.get("lower_bound", 0),
                    "upper": pred.get("upper_bound", 0)
                },
                contributing_factors={
                    "trend": forecast_result.get("metadata", {}).get("trend_direction", "unknown"),
                    "model": forecast_result.get("metadata", {}).get("model", "unknown")
                }
            )
            
            db.add(forecast)
            saved_count += 1
            
        except Exception as e:
            logger.error(f"Error saving forecast: {e}")
    
    return saved_count


# Health check task
@celery_app.task
def health_check() -> Dict[str, str]:
    """Celery health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }
