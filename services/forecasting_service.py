"""
Forecasting Service Module
==========================
Core service for loading the LSTM model and making predictions.
Handles single-step and multi-step recursive forecasting.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import tensorflow as tf

from app.config import Config
from services.preprocessing_service import PreprocessingService
from services.data_service import DataService

logger = logging.getLogger(__name__)

# Suppress TensorFlow warnings
tf.get_logger().setLevel('ERROR')


class ForecastingService:
    """Service for making stock price forecasts using LSTM model."""
    
    def __init__(
        self,
        model_path: Optional[Path] = None,
        scaler_path: Optional[Path] = None
    ):
        """
        Initialize the forecasting service.
        
        Args:
            model_path: Path to trained Keras model
            scaler_path: Path to saved scaler
        """
        self.model_path = model_path or Config.MODEL_PATH
        self.scaler_path = scaler_path or Config.SCALER_PATH
        self.window_size = Config.WINDOW_SIZE
        self.features = Config.FEATURES
        self.confidence_level = Config.CONFIDENCE_LEVEL
        
        # Initialize services
        self.data_service = DataService()
        self.preprocessing = PreprocessingService(
            window_size=self.window_size,
            features=self.features,
            scaler_path=self.scaler_path
        )
        
        # Load model
        self.model = None
        self._load_model()
        
        # Residual standard deviation for confidence intervals
        self._residual_std = None
        
    def _load_model(self) -> None:
        """Load the trained LSTM model."""
        try:
            if not Path(self.model_path).exists():
                raise FileNotFoundError(f"Model not found at {self.model_path}")
            
            self.model = tf.keras.models.load_model(self.model_path)
            logger.info(f"Model loaded from {self.model_path}")
            
            # Log model summary
            logger.info(f"Model input shape: {self.model.input_shape}")
            logger.info(f"Model output shape: {self.model.output_shape}")
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
    
    def predict_next_day(
        self,
        ticker: str,
        data: Optional[pd.DataFrame] = None
    ) -> Dict[str, Any]:
        """
        Predict the next day's OHLC values.
        
        Args:
            ticker: Stock ticker symbol
            data: Optional pre-fetched data
            
        Returns:
            Dictionary with prediction results
        """
        try:
            # Fetch data if not provided
            if data is None:
                data = self.data_service.fetch_stock_data(
                    ticker,
                    period_days=self.window_size + 60
                )
            
            # Fit scaler on the data
            self.preprocessing.fit_scaler(data)
            
            # Prepare input
            X_input = self.preprocessing.prepare_prediction_input(data)
            
            # Make prediction
            prediction_scaled = self.model.predict(X_input, verbose=0)
            
            # Inverse transform to get actual values
            prediction = self.preprocessing.inverse_transform(prediction_scaled)[0]
            predicted_close = float(prediction[0]) if len(prediction.shape) > 0 else float(prediction)
            
            # Get latest actual values for comparison
            latest = data.iloc[-1]
            latest_close = float(latest['Close'])
            
            # Calculate confidence interval (using estimated residual std)
            std_estimate = self._estimate_residual_std(data)
            
            result = {
                'ticker': ticker,
                'prediction_date': self._get_next_business_day(data.index[-1]).isoformat(),
                'predicted': {
                    'close': round(predicted_close, 2)
                },
                'confidence_interval': {
                    'close_lower': round(predicted_close - self.confidence_level * std_estimate, 2),
                    'close_upper': round(predicted_close + self.confidence_level * std_estimate, 2)
                },
                'latest_actual': {
                    'date': data.index[-1].isoformat(),
                    'close': round(latest_close, 2)
                },
                'change_predicted': round(predicted_close - latest_close, 2),
                'change_percent': round(
                    (predicted_close - latest_close) / latest_close * 100, 2
                ),
                'timestamp': datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error predicting for {ticker}: {e}")
            raise
    
    def forecast_multi_day(
        self,
        ticker: str,
        horizon: int = 5,
        data: Optional[pd.DataFrame] = None
    ) -> Dict[str, Any]:
        """
        Generate multi-day recursive forecast.
        
        Args:
            ticker: Stock ticker symbol
            horizon: Number of days to forecast
            data: Optional pre-fetched data
            
        Returns:
            Dictionary with forecast results
        """
        try:
            # Validate horizon
            horizon = max(1, min(horizon, Config.MAX_FORECAST_HORIZON))
            
            # Fetch data if not provided
            if data is None:
                data = self.data_service.fetch_stock_data(
                    ticker,
                    period_days=self.window_size + 100
                )
            
            # Fit scaler
            self.preprocessing.fit_scaler(data)
            
            # Get initial sequence (last window_size days, scaled)
            recent_data = data[self.features].iloc[-self.window_size:]
            current_sequence = self.preprocessing.transform(recent_data)
            
            # Storage for predictions
            predictions = []
            prediction_dates = []
            
            # Get the last date in data
            last_date = data.index[-1]
            
            # Recursive forecasting
            for i in range(horizon):
                # Reshape for model input
                X_input = current_sequence.reshape(1, self.window_size, len(self.features))
                
                # Predict
                pred_scaled = self.model.predict(X_input, verbose=0)
                
                # Store prediction (inverse transform)
                pred_actual = self.preprocessing.inverse_transform(pred_scaled)[0]
                pred_close = float(pred_actual[0]) if len(pred_actual.shape) > 0 else float(pred_actual)
                predictions.append(pred_close)
                
                # Calculate next business day
                next_date = self._get_next_business_day(last_date, offset=i+1)
                prediction_dates.append(next_date)
                
                # Update sequence for next iteration
                current_sequence = self.preprocessing.update_sequence_with_prediction(
                    current_sequence,
                    pred_scaled[0]
                )
            
            # Calculate confidence intervals
            std_estimate = self._estimate_residual_std(data)
            
            # Build forecast table
            forecast_table = []
            for i, (pred, date) in enumerate(zip(predictions, prediction_dates)):
                # Confidence bands widen with horizon
                horizon_factor = np.sqrt(i + 1)  # Uncertainty grows with sqrt of time
                ci_width = self.confidence_level * std_estimate * horizon_factor
                
                forecast_table.append({
                    'day': i + 1,
                    'date': date.strftime('%Y-%m-%d'),
                    'close': round(pred, 2),
                    'close_lower': round(pred - ci_width, 2),
                    'close_upper': round(pred + ci_width, 2)
                })
            
            # Calculate summary statistics
            close_predictions = predictions
            latest_close = float(data['Close'].iloc[-1])
            
            result = {
                'ticker': ticker,
                'horizon': horizon,
                'forecast': forecast_table,
                'summary': {
                    'latest_close': round(latest_close, 2),
                    'final_predicted_close': round(close_predictions[-1], 2),
                    'total_change': round(close_predictions[-1] - latest_close, 2),
                    'total_change_percent': round(
                        (close_predictions[-1] - latest_close) / latest_close * 100, 2
                    ),
                    'max_predicted_close': round(max(predictions), 2),
                    'min_predicted_close': round(min(predictions), 2),
                    'avg_predicted_close': round(float(np.mean(close_predictions)), 2),
                    'trend': 'Bullish' if close_predictions[-1] > latest_close else 'Bearish'
                },
                'confidence_level': f'{int((1 - (1 - 0.95)) * 100)}%',
                'generated_at': datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error in multi-day forecast for {ticker}: {e}")
            raise
    
    def _estimate_residual_std(self, data: pd.DataFrame) -> float:
        """
        Estimate residual standard deviation for confidence intervals.
        
        Uses historical volatility as a proxy when actual residuals aren't available.
        
        Args:
            data: Historical data
            
        Returns:
            Estimated standard deviation
        """
        if self._residual_std is not None:
            return self._residual_std
        
        # Use recent price volatility as estimate
        returns = data['Close'].pct_change().dropna()
        daily_volatility = returns.std()
        
        # Convert to price standard deviation
        recent_price = data['Close'].iloc[-1]
        price_std = daily_volatility * recent_price
        
        # Add a small buffer for model uncertainty
        return price_std * 1.5
    
    def _get_next_business_day(
        self,
        from_date: pd.Timestamp,
        offset: int = 1
    ) -> datetime:
        """
        Get the next business day.
        
        Args:
            from_date: Starting date
            offset: Number of business days ahead
            
        Returns:
            Next business day
        """
        current = pd.Timestamp(from_date)
        days_added = 0
        
        while days_added < offset:
            current += timedelta(days=1)
            if current.weekday() < 5:  # Monday = 0, Friday = 4
                days_added += 1
        
        return current.to_pydatetime()
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model."""
        if self.model is None:
            return {'status': 'not_loaded'}
        
        return {
            'status': 'loaded',
            'input_shape': str(self.model.input_shape),
            'output_shape': str(self.model.output_shape),
            'window_size': self.window_size,
            'features': self.features,
            'total_params': int(self.model.count_params())
        }
    
    def calculate_metrics(
        self,
        ticker: str,
        test_size: float = 0.2
    ) -> Dict[str, Any]:
        """
        Calculate model performance metrics on historical data.
        
        Args:
            ticker: Stock ticker symbol
            test_size: Proportion of data for testing
            
        Returns:
            Dictionary with performance metrics
        """
        try:
            # Fetch sufficient historical data
            data = self.data_service.fetch_stock_data(ticker, period_days=365 * 2)
            
            # Split data
            split_idx = int(len(data) * (1 - test_size))
            train_data = data.iloc[:split_idx]
            test_data = data.iloc[split_idx:]
            
            # Fit scaler on training data
            self.preprocessing.fit_scaler(train_data)
            
            # Scale all data
            train_scaled = self.preprocessing.transform(train_data)
            test_scaled = self.preprocessing.transform(test_data)
            
            # Create test sequences
            X_test, y_test = self.preprocessing.create_sequences(test_scaled)
            
            if len(X_test) < 10:
                raise ValueError("Insufficient test data")
            
            # Make predictions
            predictions_scaled = self.model.predict(X_test, verbose=0)
            
            # Inverse transform
            predictions = self.preprocessing.inverse_transform(predictions_scaled)
            actuals = self.preprocessing.inverse_transform(y_test)
            
            # Extract Close price (single feature model)
            close_pred = predictions.flatten()
            close_actual = actuals.flatten()
            
            # RMSE
            rmse = float(np.sqrt(np.mean((close_actual - close_pred) ** 2)))
            
            # MAE
            mae = float(np.mean(np.abs(close_actual - close_pred)))
            
            # MAPE
            mape = float(np.mean(np.abs((close_actual - close_pred) / close_actual)) * 100)
            
            # Naive baseline RMSE (persistence model)
            naive_pred = close_actual[:-1]
            naive_actual = close_actual[1:]
            naive_rmse = float(np.sqrt(np.mean((naive_actual - naive_pred) ** 2)))
            
            # Directional accuracy
            pred_direction = np.sign(close_pred[1:] - close_pred[:-1])
            actual_direction = np.sign(close_actual[1:] - close_actual[:-1])
            directional_accuracy = float(np.mean(pred_direction == actual_direction) * 100)
            
            # Store residual std for confidence intervals
            self._residual_std = float(np.std(close_actual - close_pred))
            
            return {
                'ticker': ticker,
                'test_samples': len(X_test),
                'metrics': {
                    'rmse': round(rmse, 4),
                    'mae': round(mae, 4),
                    'mape': round(mape, 2),
                    'naive_rmse': round(naive_rmse, 4),
                    'skill_score': round((1 - rmse / naive_rmse) * 100, 2),
                    'directional_accuracy': round(directional_accuracy, 2),
                    'residual_std': round(self._residual_std, 4)
                },
                'interpretation': {
                    'beats_naive': rmse < naive_rmse,
                    'model_quality': self._interpret_skill_score(1 - rmse / naive_rmse)
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating metrics: {e}")
            raise
    
    def _interpret_skill_score(self, skill_score: float) -> str:
        """Interpret the skill score."""
        if skill_score > 0.3:
            return "Excellent - Significantly beats baseline"
        elif skill_score > 0.15:
            return "Good - Beats baseline"
        elif skill_score > 0:
            return "Fair - Slightly beats baseline"
        else:
            return "Poor - Does not beat baseline"
