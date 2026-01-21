"""
Ensemble Forecaster
Combines multiple forecasting models for robust predictions
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, List, Any
import logging

from .prophet_forecaster import ProphetForecaster
from .arima_forecaster import ARIMAForecaster

logger = logging.getLogger(__name__)


class EnsembleForecaster:
    """
    Ensemble forecasting combining Prophet, ARIMA, and Linear Regression
    
    Features:
    - Weighted averaging of multiple models
    - Automatic weight optimization based on historical performance
    - Aggregated confidence intervals
    """
    
    def __init__(
        self,
        weights: Optional[Dict[str, float]] = None,
        models: Optional[List[str]] = None
    ):
        """
        Initialize ensemble forecaster
        
        Args:
            weights: Custom weights for each model. Default: {"prophet": 0.5, "arima": 0.3, "linear": 0.2}
            models: List of models to include. Default: ["prophet", "arima", "linear"]
        """
        self.weights = weights or {
            "prophet": 0.5,
            "arima": 0.3,
            "linear": 0.2
        }
        
        self.models = models or ["prophet", "arima", "linear"]
        
        # Validate weights sum to 1.0
        weight_sum = sum(self.weights.values())
        if not np.isclose(weight_sum, 1.0):
            logger.warning(f"Weights sum to {weight_sum}, normalizing...")
            self.weights = {k: v/weight_sum for k, v in self.weights.items()}
        
        self.prophet = ProphetForecaster()
        self.arima = ARIMAForecaster()
    
    def _linear_forecast(self, series: pd.Series, periods: int = 4) -> List[float]:
        """
        Simple linear regression forecast (baseline)
        
        Args:
            series: Time series data
            periods: Number of periods to forecast
            
        Returns:
            List of predictions
        """
        if len(series) < 3:
            return [series.mean()] * periods if len(series) > 0 else [0] * periods
        
        # Use last 6 points for trend
        recent = series.tail(6).values
        n = len(recent)
        
        # Linear regression
        x_vals = np.arange(n)
        x_mean = x_vals.mean()
        y_mean = recent.mean()
        
        numerator = np.sum((x_vals - x_mean) * (recent - y_mean))
        denominator = np.sum((x_vals - x_mean) ** 2)
        
        if denominator == 0:
            slope = 0
        else:
            slope = numerator / denominator
        
        intercept = y_mean - slope * x_mean
        
        # Generate forecast
        forecast = []
        for i in range(1, periods + 1):
            pred = intercept + slope * (n + i - 1)
            forecast.append(max(0, pred))
        
        return forecast
    
    def forecast(
        self,
        state: Optional[str] = None,
        lga: Optional[str] = None,
        archetype: Optional[str] = None,
        weeks_ahead: int = 4,
        include_individual_models: bool = False
    ) -> Dict[str, Any]:
        """
        Generate ensemble forecast
        
        Args:
            state: Filter by state
            lga: Filter by LGA
            archetype: Filter by conflict type
            weeks_ahead: Number of weeks to forecast
            include_individual_models: Return individual model predictions
            
        Returns:
            Dictionary with ensemble forecast and metadata
        """
        individual_forecasts = {}
        errors = {}
        
        # Prophet forecast
        if "prophet" in self.models:
            try:
                prophet_result = self.prophet.forecast(
                    state=state,
                    lga=lga,
                    archetype=archetype,
                    weeks_ahead=weeks_ahead
                )
                if "error" not in prophet_result:
                    individual_forecasts["prophet"] = prophet_result["forecast"]
                else:
                    errors["prophet"] = prophet_result["error"]
            except Exception as e:
                logger.error(f"Prophet forecast failed: {e}")
                errors["prophet"] = str(e)
        
        # ARIMA forecast
        if "arima" in self.models:
            try:
                arima_result = self.arima.forecast(
                    state=state,
                    lga=lga,
                    archetype=archetype,
                    weeks_ahead=weeks_ahead
                )
                if "error" not in arima_result:
                    individual_forecasts["arima"] = arima_result["forecast"]
                else:
                    errors["arima"] = arima_result["error"]
            except Exception as e:
                logger.error(f"ARIMA forecast failed: {e}")
                errors["arima"] = str(e)
        
        # Linear forecast
        if "linear" in self.models:
            try:
                # Load data for linear regression
                series = self.arima.load_data(state=state, lga=lga, archetype=archetype)
                if not series.empty:
                    linear_predictions = self._linear_forecast(series, periods=weeks_ahead)
                    
                    # Format as forecast list
                    last_date = series.index[-1]
                    individual_forecasts["linear"] = [
                        {
                            "date": (last_date + pd.Timedelta(weeks=i+1)).isoformat(),
                            "predicted_incidents": round(pred, 1),
                            "lower_bound": round(pred * 0.8, 1),  # Rough CI
                            "upper_bound": round(pred * 1.2, 1)
                        }
                        for i, pred in enumerate(linear_predictions)
                    ]
            except Exception as e:
                logger.error(f"Linear forecast failed: {e}")
                errors["linear"] = str(e)
        
        # Check if we have any successful forecasts
        if not individual_forecasts:
            return {
                "error": "All forecasting models failed",
                "errors": errors,
                "forecast": []
            }
        
        # Combine forecasts using weighted average
        ensemble_predictions = []
        
        for week_idx in range(weeks_ahead):
            weighted_sum = 0
            weight_total = 0
            lower_bounds = []
            upper_bounds = []
            dates = []
            
            for model_name, forecast_list in individual_forecasts.items():
                if week_idx < len(forecast_list):
                    prediction = forecast_list[week_idx]
                    weight = self.weights.get(model_name, 0)
                    
                    weighted_sum += prediction["predicted_incidents"] * weight
                    weight_total += weight
                    lower_bounds.append(prediction["lower_bound"])
                    upper_bounds.append(prediction["upper_bound"])
                    dates.append(prediction["date"])
            
            if weight_total > 0:
                ensemble_predictions.append({
                    "date": dates[0] if dates else None,
                    "predicted_incidents": round(weighted_sum / weight_total, 1),
                    "lower_bound": round(min(lower_bounds), 1) if lower_bounds else 0,
                    "upper_bound": round(max(upper_bounds), 1) if upper_bounds else 0,
                    "models_used": len(individual_forecasts),
                    "confidence_interval_width": round(
                        max(upper_bounds) - min(lower_bounds), 1
                    ) if lower_bounds and upper_bounds else 0
                })
        
        result = {
            "forecast": ensemble_predictions,
            "metadata": {
                "model": "Ensemble",
                "component_models": list(individual_forecasts.keys()),
                "weights": {k: v for k, v in self.weights.items() if k in individual_forecasts},
                "state": state,
                "lga": lga,
                "archetype": archetype,
                "forecast_horizon_weeks": weeks_ahead,
                "models_succeeded": len(individual_forecasts),
                "models_failed": len(errors)
            }
        }
        
        if errors:
            result["metadata"]["errors"] = errors
        
        if include_individual_models:
            result["individual_forecasts"] = individual_forecasts
        
        return result
    
    def optimize_weights(
        self,
        historical_data: pd.Series,
        validation_weeks: int = 8
    ) -> Dict[str, float]:
        """
        Optimize ensemble weights based on historical performance
        
        Args:
            historical_data: Historical time series
            validation_weeks: Number of weeks to use for validation
            
        Returns:
            Optimized weights dictionary
        """
        # TODO: Implement cross-validation and weight optimization
        # For now, return default weights
        logger.warning("Weight optimization not yet implemented, using default weights")
        return self.weights
