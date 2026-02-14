"""
Preprocessing Service Module
============================
Handles data preprocessing exactly as in the training notebook.
Ensures consistency between training and inference pipelines.
"""

import logging
from typing import Tuple, Optional
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import joblib

logger = logging.getLogger(__name__)


class PreprocessingService:
    """Service for preprocessing stock data for LSTM model."""
    
    def __init__(
        self,
        window_size: int = 60,
        features: list = None,
        scaler_path: Optional[Path] = None
    ):
        """
        Initialize the preprocessing service.
        
        Args:
            window_size: Lookback window for sequences
            features: List of feature names in order
            scaler_path: Path to saved scaler (or None to create new)
        """
        self.window_size = window_size
        self.features = features or ['Open', 'High', 'Low', 'Close']
        self.num_features = len(self.features)
        self.scaler = None
        self.scaler_path = scaler_path
        self._is_fitted = False
        
        # Try to load existing scaler
        if scaler_path and Path(scaler_path).exists():
            self.load_scaler(scaler_path)
    
    def fit_scaler(self, data: pd.DataFrame) -> 'PreprocessingService':
        """
        Fit the MinMaxScaler on training data.
        
        Args:
            data: DataFrame with OHLC columns
            
        Returns:
            Self for method chaining
        """
        try:
            # Ensure correct column order
            data_ordered = data[self.features].copy()
            
            # Create and fit scaler
            self.scaler = MinMaxScaler(feature_range=(0, 1))
            self.scaler.fit(data_ordered.values)
            self._is_fitted = True
            
            logger.info(f"Scaler fitted on {len(data)} samples")
            return self
            
        except Exception as e:
            logger.error(f"Error fitting scaler: {e}")
            raise
    
    def save_scaler(self, path: Optional[Path] = None) -> None:
        """
        Save the scaler to disk.
        
        Args:
            path: Path to save scaler (uses default if None)
        """
        if not self._is_fitted:
            raise ValueError("Scaler not fitted. Call fit_scaler first.")
        
        save_path = path or self.scaler_path
        if save_path:
            joblib.dump(self.scaler, save_path)
            logger.info(f"Scaler saved to {save_path}")
    
    def load_scaler(self, path: Path) -> None:
        """
        Load a fitted scaler from disk.
        
        Args:
            path: Path to saved scaler
        """
        try:
            self.scaler = joblib.load(path)
            self._is_fitted = True
            logger.info(f"Scaler loaded from {path}")
        except Exception as e:
            logger.warning(f"Could not load scaler from {path}: {e}")
            self._is_fitted = False
    
    def transform(self, data: pd.DataFrame) -> np.ndarray:
        """
        Scale the data using fitted scaler.
        
        Args:
            data: DataFrame with OHLC columns
            
        Returns:
            Scaled numpy array
        """
        if not self._is_fitted:
            raise ValueError("Scaler not fitted. Call fit_scaler first.")
        
        data_ordered = data[self.features].copy()
        return self.scaler.transform(data_ordered.values)
    
    def inverse_transform(self, data: np.ndarray) -> np.ndarray:
        """
        Inverse scale the data back to original values.
        
        Args:
            data: Scaled numpy array
            
        Returns:
            Unscaled numpy array
        """
        if not self._is_fitted:
            raise ValueError("Scaler not fitted. Call fit_scaler first.")
        
        return self.scaler.inverse_transform(data)
    
    def create_sequences(
        self,
        data: np.ndarray,
        window_size: Optional[int] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Create sliding window sequences for LSTM input.
        
        This exactly mirrors the create_sequences_multi function from training.
        
        Args:
            data: Scaled data array
            window_size: Override default window size
            
        Returns:
            Tuple of (X, y) arrays
        """
        ws = window_size or self.window_size
        X = []
        y = []
        
        for i in range(ws, len(data)):
            X.append(data[i - ws:i])
            y.append(data[i])
        
        return np.array(X), np.array(y)
    
    def prepare_prediction_input(
        self,
        data: pd.DataFrame,
        window_size: Optional[int] = None
    ) -> np.ndarray:
        """
        Prepare input data for making a prediction.
        
        Takes the last window_size rows of data, scales them,
        and reshapes for model input.
        
        Args:
            data: DataFrame with OHLC columns
            window_size: Override default window size
            
        Returns:
            Numpy array shaped (1, window_size, num_features)
        """
        ws = window_size or self.window_size
        
        if len(data) < ws:
            raise ValueError(
                f"Insufficient data. Need at least {ws} rows, got {len(data)}"
            )
        
        # Get last window_size rows
        recent_data = data[self.features].iloc[-ws:].copy()
        
        # Scale the data
        if not self._is_fitted:
            # If no scaler, fit on available data (for dynamic scaling)
            self.fit_scaler(data)
        
        scaled_data = self.transform(recent_data)
        
        # Reshape for LSTM: (batch_size, timesteps, features)
        return scaled_data.reshape(1, ws, self.num_features)
    
    def update_sequence_with_prediction(
        self,
        current_sequence: np.ndarray,
        new_prediction: np.ndarray
    ) -> np.ndarray:
        """
        Update the sequence by removing oldest row and adding new prediction.
        
        Used for recursive multi-step forecasting.
        
        Args:
            current_sequence: Current input sequence (window_size, num_features)
            new_prediction: New prediction to append (num_features,)
            
        Returns:
            Updated sequence
        """
        # Remove first row and append new prediction
        return np.vstack((current_sequence[1:], new_prediction.reshape(1, -1)))
    
    def calculate_returns(self, data: pd.DataFrame) -> pd.Series:
        """
        Calculate daily returns from closing prices.
        
        Args:
            data: DataFrame with Close column
            
        Returns:
            Series of daily returns
        """
        return data['Close'].pct_change().dropna()
    
    def calculate_log_returns(self, data: pd.DataFrame) -> pd.Series:
        """
        Calculate logarithmic returns.
        
        Args:
            data: DataFrame with Close column
            
        Returns:
            Series of log returns
        """
        return np.log(data['Close'] / data['Close'].shift(1)).dropna()
    
    @property
    def is_fitted(self) -> bool:
        """Check if scaler is fitted."""
        return self._is_fitted
    
    def get_scaler_params(self) -> dict:
        """Get scaler parameters for debugging."""
        if not self._is_fitted:
            return {}
        
        return {
            'data_min': self.scaler.data_min_.tolist(),
            'data_max': self.scaler.data_max_.tolist(),
            'scale': self.scaler.scale_.tolist(),
            'min': self.scaler.min_.tolist()
        }
