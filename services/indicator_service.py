"""
Indicator Service Module
========================
Calculates technical indicators for stock analysis.
"""

import logging
from typing import Dict, Any, Optional

import numpy as np
import pandas as pd

from app.config import Config

logger = logging.getLogger(__name__)


class IndicatorService:
    """Service for calculating technical indicators."""
    
    def __init__(self):
        """Initialize the indicator service."""
        self.ma_short = Config.MA_SHORT
        self.ma_long = Config.MA_LONG
        self.volatility_window = Config.VOLATILITY_WINDOW
    
    def calculate_all_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate all technical indicators.
        
        Args:
            data: DataFrame with OHLC data
            
        Returns:
            DataFrame with added indicator columns
        """
        df = data.copy()
        
        # Moving Averages
        df['MA20'] = df['Close'].rolling(window=self.ma_short).mean()
        df['MA50'] = df['Close'].rolling(window=self.ma_long).mean()
        
        # Daily Returns
        df['Return'] = df['Close'].pct_change()
        
        # Rolling Volatility
        df['Volatility'] = df['Return'].rolling(window=self.volatility_window).std()
        
        # Annualized Volatility
        df['Volatility_Annual'] = df['Volatility'] * np.sqrt(252)
        
        # RSI (14-day)
        df['RSI'] = self._calculate_rsi(df['Close'], period=14)
        
        # Bollinger Bands
        df['BB_Middle'] = df['Close'].rolling(window=20).mean()
        bb_std = df['Close'].rolling(window=20).std()
        df['BB_Upper'] = df['BB_Middle'] + (2 * bb_std)
        df['BB_Lower'] = df['BB_Middle'] - (2 * bb_std)
        
        # MACD
        df['EMA12'] = df['Close'].ewm(span=12, adjust=False).mean()
        df['EMA26'] = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = df['EMA12'] - df['EMA26']
        df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']
        
        return df
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """
        Calculate Relative Strength Index.
        
        Args:
            prices: Price series
            period: RSI period
            
        Returns:
            RSI series
        """
        delta = prices.diff()
        
        gain = delta.where(delta > 0, 0)
        loss = (-delta).where(delta < 0, 0)
        
        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def get_trend_signal(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Determine trend signal based on MA crossover.
        
        Args:
            data: DataFrame with calculated indicators
            
        Returns:
            Dictionary with trend signal information
        """
        df = data.copy()
        
        # Ensure MAs are calculated
        if 'MA20' not in df.columns:
            df['MA20'] = df['Close'].rolling(window=self.ma_short).mean()
        if 'MA50' not in df.columns:
            df['MA50'] = df['Close'].rolling(window=self.ma_long).mean()
        
        latest = df.iloc[-1]
        previous = df.iloc[-5] if len(df) > 5 else df.iloc[0]
        
        ma20_current = latest['MA20']
        ma50_current = latest['MA50']
        
        # Determine trend
        if pd.isna(ma20_current) or pd.isna(ma50_current):
            signal = 'Neutral'
            strength = 0
        elif ma20_current > ma50_current:
            signal = 'Bullish'
            strength = min(100, ((ma20_current - ma50_current) / ma50_current) * 100 * 10)
        else:
            signal = 'Bearish'
            strength = min(100, ((ma50_current - ma20_current) / ma50_current) * 100 * 10)
        
        # Check for recent crossover
        crossover = None
        if len(df) >= 5:
            ma20_prev = previous['MA20']
            ma50_prev = previous['MA50']
            
            if pd.notna(ma20_prev) and pd.notna(ma50_prev):
                if ma20_prev < ma50_prev and ma20_current > ma50_current:
                    crossover = 'Golden Cross (Bullish)'
                elif ma20_prev > ma50_prev and ma20_current < ma50_current:
                    crossover = 'Death Cross (Bearish)'
        
        return {
            'signal': signal,
            'strength': round(float(strength), 1),
            'ma20': round(float(ma20_current), 2) if pd.notna(ma20_current) else None,
            'ma50': round(float(ma50_current), 2) if pd.notna(ma50_current) else None,
            'crossover': crossover,
            'price_vs_ma20': 'Above' if latest['Close'] > ma20_current else 'Below',
            'price_vs_ma50': 'Above' if latest['Close'] > ma50_current else 'Below'
        }
    
    def get_volatility_metrics(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate volatility metrics.
        
        Args:
            data: DataFrame with price data
            
        Returns:
            Dictionary with volatility metrics
        """
        df = data.copy()
        
        # Calculate returns if not present
        if 'Return' not in df.columns:
            df['Return'] = df['Close'].pct_change()
        
        returns = df['Return'].dropna()
        
        # Daily volatility
        daily_vol = returns.std()
        
        # Annualized volatility
        annual_vol = daily_vol * np.sqrt(252)
        
        # Rolling volatilities
        vol_20d = returns.rolling(20).std().iloc[-1] * np.sqrt(252)
        vol_60d = returns.rolling(60).std().iloc[-1] * np.sqrt(252) if len(returns) >= 60 else None
        
        # Value at Risk (95%)
        var_95 = np.percentile(returns, 5)
        
        # Maximum drawdown
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdowns = (cumulative - running_max) / running_max
        max_drawdown = drawdowns.min()
        
        return {
            'daily_volatility': round(float(daily_vol) * 100, 2),
            'annual_volatility': round(float(annual_vol) * 100, 2),
            'volatility_20d': round(float(vol_20d) * 100, 2) if pd.notna(vol_20d) else None,
            'volatility_60d': round(float(vol_60d) * 100, 2) if vol_60d and pd.notna(vol_60d) else None,
            'var_95': round(float(var_95) * 100, 2),
            'max_drawdown': round(float(max_drawdown) * 100, 2),
            'interpretation': self._interpret_volatility(annual_vol)
        }
    
    def _interpret_volatility(self, annual_vol: float) -> str:
        """Interpret volatility level."""
        vol_pct = annual_vol * 100
        if vol_pct < 15:
            return "Low volatility - Relatively stable"
        elif vol_pct < 25:
            return "Moderate volatility - Normal market conditions"
        elif vol_pct < 40:
            return "High volatility - Increased uncertainty"
        else:
            return "Very high volatility - Extreme market conditions"
    
    def get_returns_statistics(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate returns statistics.
        
        Args:
            data: DataFrame with price data
            
        Returns:
            Dictionary with returns statistics
        """
        df = data.copy()
        
        if 'Return' not in df.columns:
            df['Return'] = df['Close'].pct_change()
        
        returns = df['Return'].dropna()
        
        # Basic statistics
        mean_return = returns.mean()
        median_return = returns.median()
        std_return = returns.std()
        
        # Distribution characteristics
        skewness = returns.skew()
        kurtosis = returns.kurtosis()
        
        # Positive/negative days
        positive_days = (returns > 0).sum()
        negative_days = (returns < 0).sum()
        total_days = len(returns)
        
        # Best and worst days
        best_day = returns.max()
        worst_day = returns.min()
        
        return {
            'mean_daily_return': round(float(mean_return) * 100, 4),
            'median_daily_return': round(float(median_return) * 100, 4),
            'std_daily_return': round(float(std_return) * 100, 4),
            'annualized_return': round(float(mean_return * 252) * 100, 2),
            'skewness': round(float(skewness), 3),
            'kurtosis': round(float(kurtosis), 3),
            'positive_days': int(positive_days),
            'negative_days': int(negative_days),
            'positive_ratio': round(float(positive_days / total_days) * 100, 1),
            'best_day': round(float(best_day) * 100, 2),
            'worst_day': round(float(worst_day) * 100, 2),
            'total_days': int(total_days)
        }
    
    def get_support_resistance(
        self,
        data: pd.DataFrame,
        lookback: int = 20
    ) -> Dict[str, Any]:
        """
        Calculate support and resistance levels.
        
        Args:
            data: DataFrame with OHLC data
            lookback: Number of days for calculation
            
        Returns:
            Dictionary with support/resistance levels
        """
        recent = data.tail(lookback)
        
        # Simple pivot points
        high = recent['High'].max()
        low = recent['Low'].min()
        close = data['Close'].iloc[-1]
        
        pivot = (high + low + close) / 3
        r1 = 2 * pivot - low
        s1 = 2 * pivot - high
        r2 = pivot + (high - low)
        s2 = pivot - (high - low)
        
        return {
            'pivot': round(float(pivot), 2),
            'resistance_1': round(float(r1), 2),
            'resistance_2': round(float(r2), 2),
            'support_1': round(float(s1), 2),
            'support_2': round(float(s2), 2),
            'recent_high': round(float(high), 2),
            'recent_low': round(float(low), 2),
            'lookback_days': lookback
        }
    
    def get_rsi_signal(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Get RSI-based signal.
        
        Args:
            data: DataFrame with RSI calculated
            
        Returns:
            Dictionary with RSI signal
        """
        if 'RSI' not in data.columns:
            data = data.copy()
            data['RSI'] = self._calculate_rsi(data['Close'])
        
        rsi = data['RSI'].iloc[-1]
        
        if pd.isna(rsi):
            return {'rsi': None, 'signal': 'Insufficient data'}
        
        if rsi >= 70:
            signal = 'Overbought'
            interpretation = 'Stock may be overvalued, potential pullback'
        elif rsi <= 30:
            signal = 'Oversold'
            interpretation = 'Stock may be undervalued, potential bounce'
        elif rsi >= 60:
            signal = 'Bullish'
            interpretation = 'Momentum favors bulls'
        elif rsi <= 40:
            signal = 'Bearish'
            interpretation = 'Momentum favors bears'
        else:
            signal = 'Neutral'
            interpretation = 'No clear momentum signal'
        
        return {
            'rsi': round(float(rsi), 2),
            'signal': signal,
            'interpretation': interpretation
        }
    
    def get_chart_data(
        self,
        data: pd.DataFrame,
        days: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Prepare data for chart visualization.
        
        Args:
            data: DataFrame with OHLC and indicators
            days: Number of days to include (None for all)
            
        Returns:
            Dictionary with chart-ready data
        """
        df = self.calculate_all_indicators(data)
        
        if days:
            df = df.tail(days)
        
        # Convert to JSON-serializable format
        chart_data = {
            'dates': df.index.strftime('%Y-%m-%d').tolist(),
            'ohlc': {
                'open': df['Open'].round(2).tolist(),
                'high': df['High'].round(2).tolist(),
                'low': df['Low'].round(2).tolist(),
                'close': df['Close'].round(2).tolist()
            },
            'indicators': {
                'ma20': df['MA20'].round(2).fillna(0).tolist(),
                'ma50': df['MA50'].round(2).fillna(0).tolist(),
                'bb_upper': df['BB_Upper'].round(2).fillna(0).tolist(),
                'bb_middle': df['BB_Middle'].round(2).fillna(0).tolist(),
                'bb_lower': df['BB_Lower'].round(2).fillna(0).tolist()
            },
            'volatility': df['Volatility'].fillna(0).multiply(100).round(2).tolist(),
            'returns': df['Return'].fillna(0).multiply(100).round(2).tolist(),
            'rsi': df['RSI'].fillna(50).round(2).tolist()
        }
        
        return chart_data
