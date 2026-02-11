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
import warnings
import pickle
import os
from pathlib import Path

from app.db.database import engine
from app.core.config import settings

logger = logging.getLogger(__name__)

# Suppress Prophet's stan_backend warnings
warnings.filterwarnings('ignore', category=FutureWarning, module='prophet')
warnings.filterwarnings('ignore', message='.*stan_backend.*')


class ProphetForecaster:
    """
    Facebook Prophet implementation for conflict forecasting
    
    Features:
    - Automatic seasonality detection (yearly patterns)
    - Trend changepoint detection
    - Confidence intervals
    - Handles missing data
    """
    
    def __init__(self, models_directory: Optional[str] = None):
        self.model = None
        self.forecast_result = None
        
        # Use configured models directory (Railway persistent volume or override)
        self.models_directory = Path(models_directory or settings.MODELS_DIR)
        
        # Ensure models directory exists with parent creation
        try:
            self.models_directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"ProphetForecaster initialized with models directory: {self.models_directory}")
            
            # Verify directory is writable
            test_file = self.models_directory / ".write_test"
            test_file.touch()
            test_file.unlink()
            logger.info("Models directory is writable")
            
        except OSError as e:
            if "Read-only file system" in str(e) and str(self.models_directory).startswith("/app"):
                # This is expected in local development - /app doesn't exist locally
                logger.warning(f"Railway persistent volume path {self.models_directory} not available locally")
                # Fall back to local saved_models directory
                self.models_directory = Path("saved_models")
                self.models_directory.mkdir(parents=True, exist_ok=True)
                logger.info(f"Using local models directory: {self.models_directory}")
            elif "Permission denied" in str(e):
                # Railway permission issue - fall back to in-memory only mode
                logger.warning(f"Models directory permission denied: {e}. Using in-memory only mode.")
                self.models_directory = None  # Disable persistent storage
            else:
                logger.error(f"Failed to create or access models directory {self.models_directory}: {e}")
                # Fall back to in-memory mode instead of raising error
                logger.warning("Falling back to in-memory only mode for Prophet models.")
                self.models_directory = None
        
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
            # Ensure timestamps are timezone-naive for Prophet
            try:
                if pd.api.types.is_datetime64tz_dtype(df['ds']):
                    df['ds'] = df['ds'].dt.tz_convert(None)
            except Exception:
                pass
            df['y'] = df['y'].astype(int)

            # Ensure weekly frequency is set to keep downstream models from dropping the index
            df = df.set_index('ds').asfreq('W').reset_index()

            # Fill missing weekly counts with 0 to avoid NaNs for sparse locations
            if 'y' in df.columns:
                df['y'] = df['y'].fillna(0)

            # Ensure there are at least two data points; if not, synthesize recent weeks with zeros
            non_na_points = df['y'].notna().sum() if 'y' in df.columns else 0
            if non_na_points < 2:
                logger.warning(f"Insufficient weekly data ({non_na_points} points) for filters: {params}. Synthesizing minimal series.")
                # Create a minimal weekly series (8 weeks) ending this week with zeros
                last_week = pd.Timestamp(datetime.utcnow()).to_period('W').end_time
                weeks = pd.date_range(end=last_week, periods=8, freq='W')
                synth_df = pd.DataFrame({'ds': weeks, 'y': [0] * len(weeks)})
                df = synth_df

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

        try:
            # Prophet 1.1+ compatibility: Don't force backend, let Prophet auto-detect
            # Remove manual backend setting that causes stan_backend attribute errors
            logger.info("Initializing Prophet with auto-detected backend (Python 3.11/Prophet 1.1+ compatible)")

            self.model = Prophet(
                yearly_seasonality=yearly_seasonality,
                weekly_seasonality=weekly_seasonality,
                daily_seasonality=False,
                changepoint_prior_scale=changepoint_prior_scale,
                interval_width=0.95,  # 95% confidence intervals
                **kwargs
            )

            logger.info("Training Prophet model...")
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                self.model.fit(df)
            logger.info("Model training complete")

        except AttributeError as e:
            if 'stan_backend' in str(e):
                logger.warning("Prophet backend attribute error - using compatibility fallback...")
                # Fallback for older Prophet versions or edge cases
                try:
                    import os
                    # Clear any problematic backend environment variables
                    if 'PROPHET_STAN_BACKEND' in os.environ:
                        del os.environ['PROPHET_STAN_BACKEND']
                    
                    # Try with minimal Prophet configuration
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        self.model = Prophet(
                            yearly_seasonality=yearly_seasonality,
                            weekly_seasonality=weekly_seasonality,
                            daily_seasonality=False,
                            changepoint_prior_scale=changepoint_prior_scale,
                            interval_width=0.95,
                            **kwargs
                        )
                        self.model.fit(df)
                    logger.info("Model training complete (compatibility mode)")
                except Exception as fallback_error:
                    logger.error(f"Prophet compatibility fallback failed: {fallback_error}")
                    raise ValueError(f"Unable to initialize Prophet model: {fallback_error}")
            else:
                logger.error(f"Unexpected AttributeError in Prophet training: {e}")
                raise
    
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
        return_historical: bool = False,
        use_cached_model: bool = True
    ) -> Dict[str, Any]:
        """
        End-to-end forecasting: load data, train, predict
        
        Args:
            state: Filter by state
            lga: Filter by LGA  
            archetype: Filter by conflict type
            weeks_ahead: Number of weeks to forecast
            return_historical: Include historical fitted values
            use_cached_model: Whether to use saved models if available
            
        Returns:
            Dictionary with forecast data and metadata
        """
        import time
        start_time = time.time()
        
        # Load data
        df = self.prepare_data(state=state, lga=lga, archetype=archetype)
        
        if df.empty:
            return {
                "error": "No historical data available",
                "forecast": [],
                "metadata": {"state": state, "lga": lga, "computation_time_seconds": 0}
            }
        
        # Generate model name for caching
        model_name = f"prophet_"
        if state:
            model_name += f"state_{state.lower().replace(' ', '_')}"
        if lga:
            model_name += f"_lga_{lga.lower().replace(' ', '_')}"
        if archetype:
            model_name += f"_arch_{archetype.lower().replace(' ', '_')}"
        
        # Get or train model
        if use_cached_model:
            model_ready = self.get_or_train_model(
                model_name=model_name,
                df=df,
                yearly_seasonality=True,
                weekly_seasonality=False,
                changepoint_prior_scale=0.05
            )
        else:
            # Train fresh model
            try:
                self.train(df)
                model_ready = True
                logger.info(f"Trained fresh model for {model_name}")
            except Exception as e:
                logger.error(f"Fresh model training failed: {e}")
                model_ready = False
        
        if not model_ready:
            return {
                "error": "Failed to train or load model",
                "forecast": [],
                "metadata": {"state": state, "lga": lga, "model_name": model_name, "computation_time_seconds": 0}
            }
        
        # Generate predictions
        try:
            forecast = self.predict(periods=weeks_ahead, freq='W')
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return {
                "error": f"Prediction failed: {str(e)}",
                "forecast": [],
                "metadata": {"state": state, "lga": lga, "model_name": model_name, "computation_time_seconds": 0}
            }
        
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
        
        # Calculate computation time
        computation_time = time.time() - start_time
        
        result = {
            "forecast": predictions,
            "metadata": {
                "model": "Prophet",
                "model_name": model_name,
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
                "significant_changepoints": changepoints,
                "cached_model_used": use_cached_model and self.load_model(model_name, force_retrain_on_failure=False),
                "computation_time_seconds": round(computation_time, 2)
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
        cp_dates = list(self.model.changepoints) if hasattr(self.model, 'changepoints') else []
        if len(cp_dates) > 0 and hasattr(self.model, 'params'):
            # Get delta (rate change) at each changepoint
            deltas = self.model.params['delta'].mean(axis=0)

            # Ensure deltas is a plain numpy array and compute top indices by position
            try:
                import numpy as _np
                deltas_arr = _np.asarray(deltas)
                top_indices = _np.abs(deltas_arr).argsort()[-top_n:][::-1]
            except Exception:
                top_indices = list(range(min(top_n, len(cp_dates))))

            for idx in top_indices:
                # idx is positional index into cp_dates
                if idx < len(cp_dates):
                    try:
                        cp_date = cp_dates[int(idx)]
                        magnitude = float(deltas_arr[int(idx)]) if 'deltas_arr' in locals() else float(deltas[int(idx)])
                        changepoints.append({
                            "date": pd.to_datetime(cp_date).isoformat(),
                            "magnitude": magnitude,
                            "direction": "increase" if magnitude > 0 else "decrease"
                        })
                    except Exception:
                        continue
        
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
    
    def save_model(self, model_name: str, include_metadata: bool = True) -> str:
        """
        Save trained Prophet model to disk with migration-safe format
        
        Args:
            model_name: Name for the saved model file
            include_metadata: Whether to include training metadata
            
        Returns:
            Path to the saved model file, or None if in-memory mode
        """
        if self.model is None:
            raise ValueError("No trained model to save")
        
        # Check if we're in in-memory mode (no persistent storage)
        if self.models_directory is None:
            logger.info(f"Model {model_name} kept in memory only (no persistent storage available)")
            return "memory_only"
        
        model_path = self.models_directory / f"{model_name}.pkl"
        
        # Create model data dictionary
        model_data = {
            "model": self.model,
            "saved_at": datetime.now().isoformat(),
            "prophet_version": Prophet.__version__ if hasattr(Prophet, '__version__') else "unknown"
        }
        
        if include_metadata and self.forecast_result is not None:
            model_data["last_forecast"] = self.forecast_result.tail(1).to_dict('records') if not self.forecast_result.empty else []
        
        try:
            with open(model_path, 'wb') as f:
                pickle.dump(model_data, f)
            
            logger.info(f"Model saved successfully to {model_path}")
            return str(model_path)
            
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
            raise
    
    def load_model(self, model_name: str, force_retrain_on_failure: bool = True) -> bool:
        """
        Load saved Prophet model with automatic training trigger for missing models
        
        Args:
            model_name: Name of the saved model file
            force_retrain_on_failure: Whether to retrain if loading fails (always True for persistent volume)
            
        Returns:
            True if model loaded successfully, False if training is needed
        """
        # Check if we're in in-memory mode (no persistent storage)
        if self.models_directory is None:
            logger.info(f"Model {model_name} not available in memory-only mode - training required")
            return False  # Signal that training is needed
        
        model_path = self.models_directory / f"{model_name}.pkl"
        
        # Check if models directory exists, create if not
        if not self.models_directory.exists():
            logger.info(f"Creating models directory: {self.models_directory}")
            self.models_directory.mkdir(parents=True, exist_ok=True)
        
        if not model_path.exists():
            logger.info(f"Model file {model_path} not found in persistent volume - triggering new training cycle")
            return False  # Signal that training is needed
        
        try:
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)
            
            # Handle different model formats
            if isinstance(model_data, dict) and 'model' in model_data:
                model = model_data['model']
                logger.info(f"Loaded model from {model_path} (saved: {model_data.get('saved_at', 'unknown')})")
            elif isinstance(model_data, Prophet):
                model = model_data
                logger.info(f"Loaded direct Prophet model from {model_path}")
            else:
                logger.error(f"Invalid model format in {model_path}")
                return False
            
            # Test for stan_backend issues
            try:
                # Try a simple prediction to test model integrity
                test_df = pd.DataFrame({
                    'ds': [pd.Timestamp.now()],
                    'y': [1]
                })
                model.predict(test_df)
                
                self.model = model
                logger.info("Model validation passed - ready for predictions")
                return True
                
            except AttributeError as e:
                if 'stan_backend' in str(e):
                    logger.warning(f"Model {model_path} has stan_backend compatibility issue - will retrain")
                    # Remove corrupted model file
                    try:
                        model_path.unlink()
                        logger.info(f"Removed corrupted model file: {model_path}")
                    except Exception as unlink_error:
                        logger.warning(f"Could not remove corrupted model file: {unlink_error}")
                    
                    return False  # Signal that retraining is needed
                else:
                    logger.error(f"Unexpected AttributeError: {e}")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to load model {model_path}: {e}")
            # Remove potentially corrupted file
            try:
                model_path.unlink()
                logger.info(f"Removed corrupted model file: {model_path}")
            except Exception:
                pass
            
            return False  # Signal that retraining is needed
    
    def _migrate_loaded_model(self, model: Prophet) -> None:
        """
        Attempt to migrate a loaded model to fix stan_backend issues
        
        Args:
            model: The loaded Prophet model with issues
        """
        try:
            # Clear any problematic environment variables
            if 'PROPHET_STAN_BACKEND' in os.environ:
                del os.environ['PROPHET_STAN_BACKEND']
            
            # Re-initialize the model's backend if possible
            if hasattr(model, 'stan_backend'):
                delattr(model, 'stan_backend')
            
            # Force re-initialization of the model's internal state
            if hasattr(model, 'params') and model.params is not None:
                # Model is fitted, try to preserve fitted parameters
                logger.info("Preserving fitted parameters during migration")
            else:
                logger.info("Model not fitted, creating fresh instance")
                
        except Exception as e:
            logger.warning(f"Model migration had issues: {e}")
            # Continue anyway - the main loading logic will handle further issues
    
    def get_or_train_model(
        self, 
        model_name: str,
        df: pd.DataFrame,
        yearly_seasonality: bool = True,
        weekly_seasonality: bool = False,
        changepoint_prior_scale: float = 0.05,
        **kwargs
    ) -> bool:
        """
        Load existing model or train new one if loading fails (always train if missing in persistent volume)
        
        Args:
            model_name: Name for saving/loading the model
            df: Training data
            yearly_seasonality: Enable yearly seasonality
            weekly_seasonality: Enable weekly seasonality
            changepoint_prior_scale: Trend flexibility
            **kwargs: Additional Prophet parameters
            
        Returns:
            True if model is ready for prediction
        """
        # Try to load existing model first
        if self.load_model(model_name, force_retrain_on_failure=True):
            return True
        
        # Always train new model if loading failed (persistent volume behavior)
        logger.info(f"Training new model {model_name} for persistent volume storage")
        try:
            self.train(
                df=df,
                yearly_seasonality=yearly_seasonality,
                weekly_seasonality=weekly_seasonality,
                changepoint_prior_scale=changepoint_prior_scale,
                **kwargs
            )
            
            # Save the newly trained model to persistent volume (if available)
            try:
                save_result = self.save_model(model_name)
                if save_result != "memory_only":
                    logger.info(f"Trained and saved new model to persistent volume: {model_name}")
                else:
                    logger.info(f"Trained new model {model_name} in memory only (no persistent storage)")
            except Exception as save_error:
                logger.error(f"Model training succeeded but save failed: {save_error}")
                # Continue anyway - model is in memory
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to train model {model_name}: {e}")
            return False
    
    def list_saved_models(self) -> List[Dict[str, Any]]:
        """
        List all saved Prophet models with metadata
        
        Returns:
            List of dictionaries with model information
        """
        models = []
        
        for model_file in self.models_directory.glob("*.pkl"):
            model_info = {
                "name": model_file.stem,
                "path": str(model_file),
                "size_bytes": model_file.stat().st_size,
                "modified": datetime.fromtimestamp(model_file.stat().st_mtime).isoformat()
            }
            
            # Try to read metadata without loading the full model
            try:
                with open(model_file, 'rb') as f:
                    # Try to read just the first part to get metadata
                    model_data = pickle.load(f)
                    
                if isinstance(model_data, dict):
                    model_info.update({
                        "saved_at": model_data.get("saved_at"),
                        "prophet_version": model_data.get("prophet_version"),
                        "format": "dict_with_metadata"
                    })
                elif isinstance(model_data, Prophet):
                    model_info.update({
                        "format": "direct_prophet",
                        "prophet_version": "unknown"
                    })
                else:
                    model_info.update({
                        "format": "unknown"
                    })
                    
            except Exception as e:
                model_info.update({
                    "format": "unreadable",
                    "error": str(e)
                })
            
            models.append(model_info)
        
        return sorted(models, key=lambda x: x["modified"], reverse=True)
