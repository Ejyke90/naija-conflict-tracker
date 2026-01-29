"""
ARIMA Time-Series Forecaster
Statistical forecasting using Auto-ARIMA for optimal parameter selection
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, List, Any, Tuple
from datetime import datetime
import logging
from sqlalchemy import text

try:
    from statsmodels.tsa.arima.model import ARIMA
    from statsmodels.tsa.stattools import adfuller
    from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False
    logging.warning("statsmodels not available, ARIMA forecaster will use fallback")

from app.db.database import engine

logger = logging.getLogger(__name__)


class ARIMAForecaster:
    """
    ARIMA (AutoRegressive Integrated Moving Average) forecaster
    
    Features:
    - Automatic stationarity testing
    - Auto parameter selection (p, d, q)
    - Confidence intervals
    - Model diagnostics (AIC, BIC)
    """
    
    def __init__(self):
        self.model = None
        self.model_fit = None
        self.order = None
        self.is_stationary = False
        
    def load_data(
        self,
        state: Optional[str] = None,
        lga: Optional[str] = None,
        archetype: Optional[str] = None
    ) -> pd.Series:
        """Load time-series data from database"""
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
            
        where_clause = "WHERE " + " AND ".join(filters) if filters else ""
        
        query = text(f"""
            SELECT 
                DATE_TRUNC('week', event_date) as week,
                COUNT(*) as incidents
            FROM conflict_events
            {where_clause}
            GROUP BY week
            ORDER BY week
        """)
        
        try:
            with engine.connect() as conn:
                df = pd.read_sql(query, conn, params=params)
            
            if df.empty:
                logger.warning(f"No data found for filters: {params}")
                return pd.Series(dtype=float)
            
            df['week'] = pd.to_datetime(df['week'])
            df.set_index('week', inplace=True)
            
            return df['incidents']
            
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            raise
    
    def test_stationarity(self, series: pd.Series, alpha: float = 0.05) -> Dict[str, Any]:
        """
        Augmented Dickey-Fuller test for stationarity
        
        Args:
            series: Time series to test
            alpha: Significance level (default 0.05)
            
        Returns:
            Dictionary with test results
        """
        if not STATSMODELS_AVAILABLE:
            logger.warning("statsmodels not available, skipping stationarity test")
            return {"is_stationary": True, "p_value": None}
        
        if len(series) < 12:
            logger.warning("Insufficient data for stationarity test")
            return {"is_stationary": False, "p_value": None, "error": "Insufficient data"}
        
        try:
            result = adfuller(series.dropna(), autolag='AIC')
            
            self.is_stationary = result[1] < alpha
            
            return {
                "is_stationary": self.is_stationary,
                "adf_statistic": result[0],
                "p_value": result[1],
                "critical_values": result[4],
                "interpretation": "Stationary" if self.is_stationary else "Non-stationary"
            }
        except Exception as e:
            logger.error(f"Stationarity test failed: {e}")
            return {"is_stationary": False, "error": str(e)}
    
    def auto_select_order(
        self,
        series: pd.Series,
        max_p: int = 3,
        max_d: int = 2,
        max_q: int = 3
    ) -> Tuple[int, int, int]:
        """
        Automatically select ARIMA order (p, d, q) using AIC
        
        Args:
            series: Time series data
            max_p: Maximum AR order
            max_d: Maximum differencing order
            max_q: Maximum MA order
            
        Returns:
            Tuple of (p, d, q)
        """
        if not STATSMODELS_AVAILABLE:
            logger.warning("Using default ARIMA order (1,1,1)")
            return (1, 1, 1)
        
        if len(series) < 20:
            logger.warning("Insufficient data for auto-selection, using (1,1,1)")
            return (1, 1, 1)
        
        best_aic = np.inf
        best_order = (1, 1, 1)
        
        # Grid search for best parameters
        for p in range(0, max_p + 1):
            for d in range(0, max_d + 1):
                for q in range(0, max_q + 1):
                    try:
                        model = ARIMA(series, order=(p, d, q))
                        model_fit = model.fit()
                        
                        if model_fit.aic < best_aic:
                            best_aic = model_fit.aic
                            best_order = (p, d, q)
                    except:
                        continue
        
        logger.info(f"Selected ARIMA order: {best_order} (AIC: {best_aic:.2f})")
        self.order = best_order
        return best_order
    
    def train(
        self,
        series: pd.Series,
        order: Optional[Tuple[int, int, int]] = None
    ) -> None:
        """
        Train ARIMA model
        
        Args:
            series: Time series data
            order: ARIMA order (p,d,q). If None, auto-select
        """
        if not STATSMODELS_AVAILABLE:
            raise ImportError("statsmodels required for ARIMA forecasting")
        
        if series.empty or len(series) < 10:
            raise ValueError("Insufficient data for ARIMA training (need at least 10 points)")
        
        # Auto-select order if not provided
        if order is None:
            order = self.auto_select_order(series)
        else:
            self.order = order
        
        # Train model
        logger.info(f"Training ARIMA{order} model...")
        self.model = ARIMA(series, order=order)
        self.model_fit = self.model.fit()
        logger.info("ARIMA model training complete")
    
    def predict(
        self,
        periods: int = 4,
        alpha: float = 0.05
    ) -> pd.DataFrame:
        """
        Generate forecast
        
        Args:
            periods: Number of periods to forecast
            alpha: Significance level for confidence intervals (default 0.05 = 95%)
            
        Returns:
            DataFrame with predictions and confidence intervals
        """
        if self.model_fit is None:
            raise ValueError("Model not trained. Call train() first.")
        
        # Generate forecast
        forecast_result = self.model_fit.get_forecast(steps=periods)
        
        # Get predictions and confidence intervals
        predictions = forecast_result.predicted_mean
        conf_int = forecast_result.conf_int(alpha=alpha)
        
        # Create result dataframe
        forecast_df = pd.DataFrame({
            'yhat': predictions.values,
            'yhat_lower': conf_int.iloc[:, 0].values,
            'yhat_upper': conf_int.iloc[:, 1].values
        })
        
        return forecast_df
    
    def forecast(
        self,
        state: Optional[str] = None,
        lga: Optional[str] = None,
        archetype: Optional[str] = None,
        weeks_ahead: int = 4,
        order: Optional[Tuple[int, int, int]] = None
    ) -> Dict[str, Any]:
        """
        End-to-end ARIMA forecasting
        
        Args:
            state: Filter by state
            lga: Filter by LGA
            archetype: Filter by conflict type
            weeks_ahead: Number of weeks to forecast
            order: ARIMA order (p,d,q). If None, auto-select
            
        Returns:
            Dictionary with forecast and model diagnostics
        """
        # Load data
        series = self.load_data(state=state, lga=lga, archetype=archetype)
        
        if series.empty or len(series) < 10:
            return {
                "error": "Insufficient data for ARIMA (need at least 10 weeks)",
                "forecast": [],
                "metadata": {"state": state, "lga": lga}
            }
        
        # Test stationarity
        stationarity = self.test_stationarity(series)
        
        # Train model
        try:
            self.train(series, order=order)
        except Exception as e:
            logger.error(f"ARIMA training failed: {e}")
            return {
                "error": f"Model training failed: {str(e)}",
                "forecast": [],
                "metadata": {"state": state, "lga": lga}
            }
        
        # Generate predictions
        forecast_df = self.predict(periods=weeks_ahead)
        
        # Format predictions
        predictions = []
        last_date = series.index[-1]
        
        for i in range(weeks_ahead):
            future_date = last_date + pd.Timedelta(weeks=i+1)
            predictions.append({
                "date": future_date.isoformat(),
                "predicted_incidents": max(0, round(forecast_df['yhat'].iloc[i], 1)),
                "lower_bound": max(0, round(forecast_df['yhat_lower'].iloc[i], 1)),
                "upper_bound": max(0, round(forecast_df['yhat_upper'].iloc[i], 1)),
                "confidence_interval_width": round(
                    forecast_df['yhat_upper'].iloc[i] - forecast_df['yhat_lower'].iloc[i], 1
                )
            })
        
        # Model diagnostics
        diagnostics = {
            "AIC": round(self.model_fit.aic, 2) if self.model_fit else None,
            "BIC": round(self.model_fit.bic, 2) if self.model_fit else None,
            "order": self.order,
            "stationarity_test": stationarity
        }
        
        return {
            "forecast": predictions,
            "metadata": {
                "model": "ARIMA",
                "state": state,
                "lga": lga,
                "archetype": archetype,
                "training_data_points": len(series),
                "training_period": {
                    "start": series.index[0].isoformat(),
                    "end": series.index[-1].isoformat()
                },
                "forecast_horizon_weeks": weeks_ahead,
                "confidence_level": 0.95,
                "diagnostics": diagnostics
            }
        }
    
    def get_model_summary(self) -> str:
        """Get detailed model summary"""
        if self.model_fit is None:
            return "Model not trained"
        
        return str(self.model_fit.summary())
