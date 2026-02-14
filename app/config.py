"""
Application Configuration Module
================================
Centralized configuration for the Stock Forecast Dashboard.
Uses environment variables with sensible defaults.
"""

import os
from pathlib import Path


class Config:
    """Base configuration class."""
    
    # Application Settings
    APP_NAME = "Stock Forecast Dashboard"
    VERSION = "1.0.0"
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
    DEBUG = os.environ.get('DEBUG', 'False').lower() in ('true', '1', 'yes')
    
    # Base Paths
    BASE_DIR = Path(__file__).resolve().parent.parent
    MODELS_DIR = BASE_DIR / 'models'
    STATIC_DIR = BASE_DIR / 'static'
    TEMPLATES_DIR = BASE_DIR / 'templates'
    
    # Model Configuration
    MODEL_PATH = MODELS_DIR / 'stock_prediction_model.keras'
    SCALER_PATH = MODELS_DIR / 'scaler.joblib'
    
    # LSTM Model Parameters (must match training)
    WINDOW_SIZE = 100  # Lookback window (days)
    FEATURES = ['Close']  # Feature order must match training - CLOSE ONLY!
    NUM_FEATURES = 1
    
    # Forecasting Parameters
    DEFAULT_FORECAST_HORIZON = 5  # Days
    MAX_FORECAST_HORIZON = 30
    MIN_FORECAST_HORIZON = 1
    CONFIDENCE_LEVEL = 1.96  # 95% confidence interval (z-score)
    
    # Data Parameters
    DEFAULT_TICKER = 'AAPL'
    DEFAULT_LOOKBACK_DAYS = 365  # Historical data to fetch
    MIN_DATA_POINTS = WINDOW_SIZE + 10  # Minimum required data
    
    # Technical Indicators
    MA_SHORT = 20  # Moving average short period
    MA_LONG = 50   # Moving average long period
    VOLATILITY_WINDOW = 20  # Rolling volatility window
    
    # API Rate Limiting
    RATE_LIMIT = os.environ.get('RATE_LIMIT', '100 per minute')
    
    # Report Settings
    REPORTS_DIR = BASE_DIR / 'reports'
    
    # Disclaimer
    DISCLAIMER = (
        "This system provides analytical forecasts based on historical patterns. "
        "It does not constitute financial advice. Past performance is not indicative "
        "of future results. Always conduct your own research before making investment decisions."
    )


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    

class TestingConfig(Config):
    """Testing configuration."""
    DEBUG = True
    TESTING = True


# Configuration mapping
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config():
    """Get configuration based on environment."""
    env = os.environ.get('FLASK_ENV', 'development')
    return config_by_name.get(env, DevelopmentConfig)
