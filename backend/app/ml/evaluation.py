"""
Model Evaluation Module
Backtesting, performance metrics, and model comparison
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
import logging

from .prophet_forecaster import ProphetForecaster
from .arima_forecaster import ARIMAForecaster
from .ensemble_forecaster import EnsembleForecaster

logger = logging.getLogger(__name__)


class ModelEvaluator:
    """
    Evaluate forecasting model performance using backtesting
    
    Metrics:
    - MAE (Mean Absolute Error)
    - RMSE (Root Mean Squared Error)
    - MAPE (Mean Absolute Percentage Error)
    - Coverage (% of actuals within confidence interval)
    - Direction Accuracy (% of correct trend direction)
    """
    
    def __init__(self):
        self.results = {}
    
    def calculate_mae(self, actual: np.ndarray, predicted: np.ndarray) -> float:
        """Mean Absolute Error"""
        return np.mean(np.abs(actual - predicted))
    
    def calculate_rmse(self, actual: np.ndarray, predicted: np.ndarray) -> float:
        """Root Mean Squared Error"""
        return np.sqrt(np.mean((actual - predicted) ** 2))
    
    def calculate_mape(self, actual: np.ndarray, predicted: np.ndarray) -> float:
        """
        Mean Absolute Percentage Error
        Handles zero values by excluding them
        """
        # Exclude zero actuals to avoid division by zero
        mask = actual != 0
        if mask.sum() == 0:
            return np.inf
        
        return np.mean(np.abs((actual[mask] - predicted[mask]) / actual[mask])) * 100
    
    def calculate_coverage(
        self,
        actual: np.ndarray,
        lower: np.ndarray,
        upper: np.ndarray
    ) -> float:
        """
        Calculate % of actual values within confidence interval
        """
        within_interval = (actual >= lower) & (actual <= upper)
        return np.mean(within_interval) * 100
    
    def calculate_direction_accuracy(
        self,
        actual: np.ndarray,
        predicted: np.ndarray
    ) -> float:
        """
        Calculate % of correct trend direction predictions
        """
        if len(actual) < 2:
            return 0.0
        
        # Calculate actual and predicted changes
        actual_diff = np.diff(actual)
        predicted_diff = np.diff(predicted)
        
        # Check if directions match (both positive, both negative, or both ~zero)
        correct_direction = np.sign(actual_diff) == np.sign(predicted_diff)
        
        return np.mean(correct_direction) * 100
    
    def backtest(
        self,
        model_func: Callable,
        series: pd.Series,
        test_size: int = 12,
        step_size: int = 4,
        **model_kwargs
    ) -> Dict[str, Any]:
        """
        Perform rolling window backtesting
        
        Args:
            model_func: Forecasting function (e.g., prophet.forecast)
            series: Historical time series
            test_size: Number of points to use for testing
            step_size: Forecast horizon for each test
            **model_kwargs: Additional arguments for model
            
        Returns:
            Dictionary with performance metrics
        """
        if len(series) < test_size + step_size:
            raise ValueError(f"Insufficient data for backtesting (need at least {test_size + step_size} points)")
        
        actuals = []
        predictions = []
        lower_bounds = []
        upper_bounds = []
        
        # Split into train and test
        train_data = series[:-test_size]
        test_data = series[-test_size:]
        
        # Rolling forecast
        for i in range(0, len(test_data) - step_size + 1, step_size):
            # Extend training data incrementally
            current_train = pd.concat([train_data, test_data[:i]]) if i > 0 else train_data
            
            # Get forecast for next step_size periods
            try:
                # This assumes model_func returns a dict with "forecast" key
                forecast_result = model_func(
                    historical_data=current_train,
                    periods=step_size,
                    **model_kwargs
                )
                
                if "error" in forecast_result or not forecast_result.get("forecast"):
                    continue
                
                # Extract predictions
                for j, pred in enumerate(forecast_result["forecast"][:step_size]):
                    if i + j < len(test_data):
                        actuals.append(test_data.iloc[i + j])
                        predictions.append(pred.get("predicted_incidents", 0))
                        lower_bounds.append(pred.get("lower_bound", 0))
                        upper_bounds.append(pred.get("upper_bound", 0))
            
            except Exception as e:
                logger.error(f"Backtest iteration failed: {e}")
                continue
        
        if not actuals or not predictions:
            return {
                "error": "Backtest failed - no predictions generated",
                "metrics": {}
            }
        
        # Convert to numpy arrays
        actuals = np.array(actuals)
        predictions = np.array(predictions)
        lower_bounds = np.array(lower_bounds)
        upper_bounds = np.array(upper_bounds)
        
        # Calculate metrics
        metrics = {
            "MAE": round(self.calculate_mae(actuals, predictions), 2),
            "RMSE": round(self.calculate_rmse(actuals, predictions), 2),
            "MAPE": round(self.calculate_mape(actuals, predictions), 2),
            "Coverage": round(self.calculate_coverage(actuals, lower_bounds, upper_bounds), 2),
            "DirectionAccuracy": round(self.calculate_direction_accuracy(actuals, predictions), 2),
            "n_predictions": len(predictions),
            "mean_actual": round(actuals.mean(), 2),
            "mean_predicted": round(predictions.mean(), 2)
        }
        
        return {
            "metrics": metrics,
            "actuals": actuals.tolist(),
            "predictions": predictions.tolist()
        }
    
    def compare_models(
        self,
        state: Optional[str] = None,
        lga: Optional[str] = None,
        test_size: int = 12
    ) -> Dict[str, Any]:
        """
        Compare Prophet, ARIMA, and Ensemble on same data
        
        Args:
            state: Filter by state
            lga: Filter by LGA
            test_size: Number of weeks for testing
            
        Returns:
            Comparison results with metrics for each model
        """
        prophet = ProphetForecaster()
        arima = ARIMAForecaster()
        ensemble = EnsembleForecaster()
        
        # Load data
        series = arima.load_data(state=state, lga=lga)
        
        if series.empty or len(series) < test_size + 8:
            return {
                "error": f"Insufficient data (need at least {test_size + 8} weeks)",
                "data_points": len(series)
            }
        
        results = {}
        
        # Test Prophet
        logger.info("Testing Prophet...")
        try:
            def prophet_wrapper(historical_data, periods, **kwargs):
                prophet_test = ProphetForecaster()
                df = pd.DataFrame({
                    'ds': historical_data.index,
                    'y': historical_data.values
                })
                prophet_test.train(df)
                forecast = prophet_test.predict(periods=periods)
                
                # Format like our forecast API
                return {
                    "forecast": [
                        {
                            "predicted_incidents": row['yhat'],
                            "lower_bound": row['yhat_lower'],
                            "upper_bound": row['yhat_upper']
                        }
                        for _, row in forecast.tail(periods).iterrows()
                    ]
                }
            
            results["Prophet"] = self.backtest(
                prophet_wrapper,
                series,
                test_size=test_size
            )
        except Exception as e:
            logger.error(f"Prophet backtest failed: {e}")
            results["Prophet"] = {"error": str(e)}
        
        # Test ARIMA
        logger.info("Testing ARIMA...")
        try:
            def arima_wrapper(historical_data, periods, **kwargs):
                arima_test = ARIMAForecaster()
                arima_test.train(historical_data)
                forecast_df = arima_test.predict(periods=periods)
                
                return {
                    "forecast": [
                        {
                            "predicted_incidents": row['yhat'],
                            "lower_bound": row['yhat_lower'],
                            "upper_bound": row['yhat_upper']
                        }
                        for _, row in forecast_df.iterrows()
                    ]
                }
            
            results["ARIMA"] = self.backtest(
                arima_wrapper,
                series,
                test_size=test_size
            )
        except Exception as e:
            logger.error(f"ARIMA backtest failed: {e}")
            results["ARIMA"] = {"error": str(e)}
        
        # Determine best model
        best_model = None
        best_mae = float('inf')
        
        for model_name, result in results.items():
            if "metrics" in result and "MAE" in result["metrics"]:
                if result["metrics"]["MAE"] < best_mae:
                    best_mae = result["metrics"]["MAE"]
                    best_model = model_name
        
        return {
            "comparison": results,
            "best_model": best_model,
            "best_mae": best_mae,
            "metadata": {
                "state": state,
                "lga": lga,
                "test_size": test_size,
                "data_points": len(series)
            }
        }
    
    def get_performance_summary(self, metrics: Dict[str, float]) -> Dict[str, str]:
        """
        Interpret performance metrics with quality ratings
        
        Args:
            metrics: Dictionary of metrics
            
        Returns:
            Human-readable performance summary
        """
        summary = {}
        
        # MAE interpretation
        mae = metrics.get("MAE", 0)
        if mae < 3:
            summary["MAE_rating"] = "Excellent"
        elif mae < 5:
            summary["MAE_rating"] = "Good"
        elif mae < 10:
            summary["MAE_rating"] = "Fair"
        else:
            summary["MAE_rating"] = "Poor"
        
        # Coverage interpretation
        coverage = metrics.get("Coverage", 0)
        if coverage >= 90:
            summary["Coverage_rating"] = "Excellent"
        elif coverage >= 80:
            summary["Coverage_rating"] = "Good"
        elif coverage >= 70:
            summary["Coverage_rating"] = "Fair"
        else:
            summary["Coverage_rating"] = "Poor"
        
        # Direction accuracy
        direction = metrics.get("DirectionAccuracy", 0)
        if direction >= 75:
            summary["Direction_rating"] = "Excellent"
        elif direction >= 65:
            summary["Direction_rating"] = "Good"
        elif direction >= 55:
            summary["Direction_rating"] = "Fair"
        else:
            summary["Direction_rating"] = "Poor"
        
        # Overall rating
        ratings = [summary["MAE_rating"], summary["Coverage_rating"], summary["Direction_rating"]]
        excellent_count = ratings.count("Excellent")
        good_count = ratings.count("Good")
        
        if excellent_count >= 2:
            summary["Overall"] = "Excellent"
        elif excellent_count + good_count >= 2:
            summary["Overall"] = "Good"
        elif "Poor" not in ratings:
            summary["Overall"] = "Fair"
        else:
            summary["Overall"] = "Poor"
        
        return summary
