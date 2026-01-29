"""
Prophet Time-Series Forecaster
Uses Facebook Prophet for conflict prediction with seasonality detection
"""

from prophet import Prophet
import pandas as pd
from sqlalchemy import text
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
import logging

from app.db.database import engine

logger = logging.getLogger(__name__)


class ProphetForecaster:
    """
    Facebook Prophet implementation for conflict forecasting
    
    Features:
    - Automatic seasonality detection (yearly patterns)
    - Trend changepoint detection
    - Confidence intervals
    - Handles missing data
    """
    
    def __init__(self):
        self.model = None
        self.forecast_result = None
        
    def prepare_data(
        self, 
        state: Optional[str] = None, 
        lga: Optional[str] = None,
        archetype: Optional[str] = None,
        min_date: Optional[datetime] = None
    ) -> pd.DataFrame:
        """
        Load and prepare time-series data from conflicts table
        
        Args:
            state: Filter by state
            lga: Filter by LGA
            archetype: Filter by conflict archetype
            min_date: Only include data from this date onwards
            
        Returns:
            DataFrame with 'ds' (date) and 'y' (incident count) columns
        """
        # Build query with optional filters
        filters = []
        params = {}
        
        if state:
            filters.append("state = :state")
            params["state"] = state
        if lga:
            filters.append("lga = :lga")
            params["lga"] = lga
        if archetype:
            filters.append("archetype = :archetype")
            params["archetype"] = archetype
        if min_date:
            filters.append("event_date >= :min_date")
            params["min_date"] = min_date
            
        where_clause = "WHERE " + " AND ".join(filters) if filters else ""
        
        query = text(f"""
            SELECT 
                DATE_TRUNC('week', event_date) as ds,
                COUNT(*) as y
            FROM conflict_events
            {where_clause}
            GROUP BY ds
            ORDER BY ds
        """)
        
        try:
            with engine.connect() as conn:
                df = pd.read_sql(query, conn, params=params)
            
            if df.empty:
                logger.warning(f"No data found for filters: {params}")
                return pd.DataFrame(columns=['ds', 'y'])
            
            df['ds'] = pd.to_datetime(df['ds'])
            df['y'] = df['y'].astype(int)
            
            logger.info(f"Loaded {len(df)} weeks of data from {df['ds'].min()} to {df['ds'].max()}")
            return df
            
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            raise
    
    def train(
        self, 
        df: pd.DataFrame,
        yearly_seasonality: bool = True,
        weekly_seasonality: bool = False,
        changepoint_prior_scale: float = 0.05,
        **kwargs
    ) -> None:
        """
        Train Prophet model on historical data
        
        Args:
            df: DataFrame with 'ds' and 'y' columns
            yearly_seasonality: Enable yearly seasonality detection
            weekly_seasonality: Enable weekly seasonality
            changepoint_prior_scale: Flexibility of trend (higher = more flexible)
            **kwargs: Additional Prophet parameters
        """
        if df.empty or len(df) < 2:
            raise ValueError("Insufficient data for training (need at least 2 data points)")
        
        self.model = Prophet(
            yearly_seasonality=yearly_seasonality,
            weekly_seasonality=weekly_seasonality,
            daily_seasonality=False,
            changepoint_prior_scale=changepoint_prior_scale,
            interval_width=0.95,  # 95% confidence intervals
            **kwargs
        )
        
        logger.info("Training Prophet model...")
        self.model.fit(df)
        logger.info("Model training complete")
    
    def predict(self, periods: int = 4, freq: str = 'W') -> pd.DataFrame:
        """
        Generate forecast for future periods
        
        Args:
            periods: Number of periods to forecast
            freq: Frequency ('W' for weeks, 'M' for months, 'D' for days)
            
        Returns:
            DataFrame with predictions and confidence intervals
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        future = self.model.make_future_dataframe(periods=periods, freq=freq)
        forecast = self.model.predict(future)
        
        self.forecast_result = forecast
        return forecast
    
    def forecast(
        self,
        state: Optional[str] = None,
        lga: Optional[str] = None,
        archetype: Optional[str] = None,
        weeks_ahead: int = 4,
        return_historical: bool = False
    ) -> Dict[str, Any]:
        """
        End-to-end forecasting: load data, train, predict
        
        Args:
            state: Filter by state
            lga: Filter by LGA  
            archetype: Filter by conflict type
            weeks_ahead: Number of weeks to forecast
            return_historical: Include historical fitted values
            
        Returns:
            Dictionary with forecast data and metadata
        """
        # Load data
        df = self.prepare_data(state=state, lga=lga, archetype=archetype)
        
        if df.empty:
            return {
                "error": "No historical data available",
                "forecast": [],
                "metadata": {"state": state, "lga": lga}
            }
        
        # Train model
        self.train(df)
        
        # Generate predictions
        forecast = self.predict(periods=weeks_ahead, freq='W')
        
        # Extract future predictions only (last N periods)
        future_forecast = forecast.tail(weeks_ahead)
        
        # Format output
        predictions = []
        for _, row in future_forecast.iterrows():
            predictions.append({
                "date": row['ds'].isoformat(),
                "predicted_incidents": max(0, round(row['yhat'], 1)),
                "lower_bound": max(0, round(row['yhat_lower'], 1)),
                "upper_bound": max(0, round(row['yhat_upper'], 1)),
                "confidence_interval_width": round(row['yhat_upper'] - row['yhat_lower'], 1)
            })
        
        # Calculate trend
        recent_trend = self._calculate_trend(forecast)
        
        # Detect changepoints
        changepoints = self._get_changepoints()
        
        result = {
            "forecast": predictions,
            "metadata": {
                "model": "Prophet",
                "state": state,
                "lga": lga,
                "archetype": archetype,
                "training_data_points": len(df),
                "training_period": {
                    "start": df['ds'].min().isoformat(),
                    "end": df['ds'].max().isoformat()
                },
                "forecast_horizon_weeks": weeks_ahead,
                "trend_direction": recent_trend,
                "confidence_level": 0.95,
                "significant_changepoints": changepoints
            }
        }
        
        if return_historical:
            historical = []
            for _, row in forecast[:-weeks_ahead].iterrows():
                historical.append({
                    "date": row['ds'].isoformat(),
                    "actual": None,  # Would need to join with original data
                    "fitted": max(0, round(row['yhat'], 1))
                })
            result["historical_fit"] = historical
        
        return result
    
    def _calculate_trend(self, forecast: pd.DataFrame) -> str:
        """Determine if trend is increasing, decreasing, or stable"""
        if forecast.empty or len(forecast) < 2:
            return "unknown"
        
        # Compare first and last trend values
        trend_start = forecast['trend'].iloc[0]
        trend_end = forecast['trend'].iloc[-1]
        
        change_pct = ((trend_end - trend_start) / trend_start * 100) if trend_start > 0 else 0
        
        if change_pct > 10:
            return "increasing"
        elif change_pct < -10:
            return "decreasing"
        else:
            return "stable"
    
    def _get_changepoints(self, top_n: int = 3) -> List[Dict[str, Any]]:
        """Get most significant trend changepoints"""
        if self.model is None or not hasattr(self.model, 'changepoints'):
            return []
        
        changepoints = []
        
        # Get changepoint dates and magnitudes
        cp_dates = self.model.changepoints
        if len(cp_dates) > 0 and hasattr(self.model, 'params'):
            # Get delta (rate change) at each changepoint
            deltas = self.model.params['delta'].mean(axis=0)
            
            # Find top N most significant changes
            top_indices = abs(deltas).argsort()[-top_n:][::-1]
            
            for idx in top_indices:
                if idx < len(cp_dates):
                    changepoints.append({
                        "date": pd.to_datetime(cp_dates[idx]).isoformat(),
                        "magnitude": float(deltas[idx]),
                        "direction": "increase" if deltas[idx] > 0 else "decrease"
                    })
        
        return changepoints
    
    def get_forecast_summary(self) -> Dict[str, Any]:
        """Get summary statistics of the forecast"""
        if self.forecast_result is None:
            return {}
        
        forecast = self.forecast_result
        
        return {
            "mean_prediction": round(forecast['yhat'].mean(), 2),
            "max_prediction": round(forecast['yhat'].max(), 2),
            "min_prediction": round(forecast['yhat'].min(), 2),
            "avg_uncertainty": round((forecast['yhat_upper'] - forecast['yhat_lower']).mean(), 2),
            "trend_component_strength": round(forecast['trend'].std(), 2)
        }
