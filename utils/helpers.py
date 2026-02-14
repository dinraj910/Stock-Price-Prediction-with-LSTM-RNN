"""
Utility helper functions for stock forecast dashboard.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, Union, List, Dict, Any


def format_currency(value: float, currency: str = "USD", decimals: int = 2) -> str:
    """
    Format a numeric value as currency string.
    
    Args:
        value: Numeric value to format
        currency: Currency symbol (default: USD)
        decimals: Number of decimal places
        
    Returns:
        Formatted currency string
    """
    if currency == "USD":
        return f"${value:,.{decimals}f}"
    return f"{value:,.{decimals}f} {currency}"


def format_percentage(value: float, decimals: int = 2) -> str:
    """
    Format a numeric value as percentage string.
    
    Args:
        value: Numeric value (e.g., 0.05 for 5%)
        decimals: Number of decimal places
        
    Returns:
        Formatted percentage string
    """
    return f"{value * 100:.{decimals}f}%"


def format_large_number(value: float) -> str:
    """
    Format large numbers with K, M, B suffixes.
    
    Args:
        value: Numeric value to format
        
    Returns:
        Formatted string with appropriate suffix
    """
    if abs(value) >= 1e9:
        return f"{value / 1e9:.2f}B"
    elif abs(value) >= 1e6:
        return f"{value / 1e6:.2f}M"
    elif abs(value) >= 1e3:
        return f"{value / 1e3:.2f}K"
    return f"{value:.2f}"


def parse_date(date_str: str, formats: List[str] = None) -> Optional[datetime]:
    """
    Parse date string trying multiple formats.
    
    Args:
        date_str: Date string to parse
        formats: List of datetime formats to try
        
    Returns:
        Parsed datetime object or None if failed
    """
    if formats is None:
        formats = [
            "%Y-%m-%d",
            "%Y/%m/%d",
            "%m/%d/%Y",
            "%d-%m-%Y",
            "%Y-%m-%d %H:%M:%S"
        ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    return None


def get_trading_days(start_date: datetime, end_date: datetime) -> int:
    """
    Calculate approximate number of trading days between dates.
    
    Args:
        start_date: Start datetime
        end_date: End datetime
        
    Returns:
        Approximate number of trading days
    """
    total_days = (end_date - start_date).days
    # Approximate: 5 trading days per 7 calendar days
    return int(total_days * 5 / 7)


def get_date_range(period: str) -> tuple:
    """
    Get date range based on period string.
    
    Args:
        period: Period string (e.g., '1mo', '3mo', '6mo', '1y', '2y')
        
    Returns:
        Tuple of (start_date, end_date) strings
    """
    end_date = datetime.now()
    
    period_mapping = {
        '1mo': timedelta(days=30),
        '3mo': timedelta(days=90),
        '6mo': timedelta(days=180),
        '1y': timedelta(days=365),
        '2y': timedelta(days=730),
        '5y': timedelta(days=1825),
        'max': timedelta(days=7300)  # ~20 years
    }
    
    delta = period_mapping.get(period.lower(), timedelta(days=365))
    start_date = end_date - delta
    
    return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers, returning default if denominator is zero.
    
    Args:
        numerator: Numerator value
        denominator: Denominator value
        default: Default value if division by zero
        
    Returns:
        Division result or default
    """
    if denominator == 0:
        return default
    return numerator / denominator


def calculate_change(current: float, previous: float) -> Dict[str, float]:
    """
    Calculate absolute and percentage change between two values.
    
    Args:
        current: Current value
        previous: Previous value
        
    Returns:
        Dictionary with 'absolute' and 'percentage' changes
    """
    absolute = current - previous
    percentage = safe_divide(absolute, previous) * 100
    
    return {
        'absolute': absolute,
        'percentage': percentage,
        'direction': 'up' if absolute > 0 else 'down' if absolute < 0 else 'unchanged'
    }


def validate_dataframe(df: pd.DataFrame, required_columns: List[str]) -> bool:
    """
    Validate that dataframe has required columns.
    
    Args:
        df: Pandas DataFrame to validate
        required_columns: List of required column names
        
    Returns:
        True if all columns present, False otherwise
    """
    if df is None or df.empty:
        return False
    
    return all(col in df.columns for col in required_columns)


def clean_ticker(ticker: str) -> str:
    """
    Clean and normalize stock ticker symbol.
    
    Args:
        ticker: Raw ticker string
        
    Returns:
        Cleaned ticker symbol
    """
    if not ticker:
        return ""
    
    # Remove whitespace and convert to uppercase
    cleaned = ticker.strip().upper()
    
    # Remove any special characters except hyphen and period
    cleaned = ''.join(c for c in cleaned if c.isalnum() or c in '.-')
    
    return cleaned


def get_trend_emoji(value: float) -> str:
    """
    Get trend indicator emoji based on value.
    
    Args:
        value: Numeric value (positive = up, negative = down)
        
    Returns:
        Unicode emoji character
    """
    if value > 0:
        return "📈"
    elif value < 0:
        return "📉"
    return "➡️"


def clamp(value: float, min_val: float, max_val: float) -> float:
    """
    Clamp a value between min and max bounds.
    
    Args:
        value: Value to clamp
        min_val: Minimum bound
        max_val: Maximum bound
        
    Returns:
        Clamped value
    """
    return max(min_val, min(value, max_val))


def moving_average(data: np.ndarray, window: int) -> np.ndarray:
    """
    Calculate simple moving average.
    
    Args:
        data: Input data array
        window: Window size for moving average
        
    Returns:
        Moving average array
    """
    if len(data) < window:
        return np.array([])
    
    return np.convolve(data, np.ones(window) / window, mode='valid')


def exponential_moving_average(data: np.ndarray, span: int) -> np.ndarray:
    """
    Calculate exponential moving average.
    
    Args:
        data: Input data array
        span: Span for EMA calculation
        
    Returns:
        EMA array
    """
    alpha = 2 / (span + 1)
    ema = np.zeros_like(data)
    ema[0] = data[0]
    
    for i in range(1, len(data)):
        ema[i] = alpha * data[i] + (1 - alpha) * ema[i-1]
    
    return ema


def generate_unique_id() -> str:
    """
    Generate a unique identifier.
    
    Returns:
        Unique ID string
    """
    import uuid
    return str(uuid.uuid4())[:8]
