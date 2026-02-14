"""
Data Service Module
===================
Handles fetching and managing stock market data via yfinance.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple

import pandas as pd
import numpy as np
import yfinance as yf

logger = logging.getLogger(__name__)


class DataService:
    """Service for fetching and managing stock market data."""
    
    # Popular stock tickers for autocomplete
    POPULAR_TICKERS = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA',
        'JPM', 'V', 'JNJ', 'WMT', 'PG', 'MA', 'HD', 'CVX',
        'MRK', 'ABBV', 'PEP', 'KO', 'COST', 'TMO', 'AVGO',
        'MCD', 'CSCO', 'ACN', 'ABT', 'LLY', 'DHR', 'TXN', 'NEE'
    ]
    
    def __init__(self):
        """Initialize the data service."""
        self._cache = {}
        self._cache_ttl = 300  # 5 minutes cache
        
    def fetch_stock_data(
        self,
        ticker: str,
        period_days: int = 365,
        include_all_columns: bool = False
    ) -> pd.DataFrame:
        """
        Fetch historical stock data from Yahoo Finance.
        
        Args:
            ticker: Stock ticker symbol
            period_days: Number of days of historical data
            include_all_columns: Whether to include volume and adjusted close
            
        Returns:
            DataFrame with OHLC data
        """
        try:
            ticker = ticker.upper().strip()
            
            # Check cache
            cache_key = f"{ticker}_{period_days}"
            if cache_key in self._cache:
                cached_data, timestamp = self._cache[cache_key]
                if (datetime.now() - timestamp).seconds < self._cache_ttl:
                    logger.info(f"Returning cached data for {ticker}")
                    return cached_data.copy()
            
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=period_days + 30)  # Extra buffer
            
            logger.info(f"Fetching data for {ticker} from {start_date} to {end_date}")
            
            # Fetch data
            stock = yf.Ticker(ticker)
            data = stock.history(start=start_date, end=end_date)
            
            if data.empty:
                raise ValueError(f"No data found for ticker: {ticker}")
            
            # Select columns
            if include_all_columns:
                columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            else:
                columns = ['Open', 'High', 'Low', 'Close']
            
            data = data[columns].copy()
            data.dropna(inplace=True)
            
            # Ensure datetime index
            data.index = pd.to_datetime(data.index)
            
            # Cache the data
            self._cache[cache_key] = (data.copy(), datetime.now())
            
            logger.info(f"Fetched {len(data)} rows for {ticker}")
            return data
            
        except Exception as e:
            logger.error(f"Error fetching data for {ticker}: {e}")
            raise
    
    def get_latest_price(self, ticker: str) -> Dict[str, Any]:
        """
        Get the latest price information for a stock.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with latest price data
        """
        try:
            ticker = ticker.upper().strip()
            stock = yf.Ticker(ticker)
            
            # Get current info
            info = stock.info
            
            # Get recent history for additional details
            history = stock.history(period='5d')
            
            if history.empty:
                raise ValueError(f"No recent data for {ticker}")
            
            latest = history.iloc[-1]
            previous = history.iloc[-2] if len(history) > 1 else latest
            
            change = latest['Close'] - previous['Close']
            change_pct = (change / previous['Close']) * 100 if previous['Close'] != 0 else 0
            
            return {
                'ticker': ticker,
                'name': info.get('shortName', ticker),
                'current_price': round(float(latest['Close']), 2),
                'open': round(float(latest['Open']), 2),
                'high': round(float(latest['High']), 2),
                'low': round(float(latest['Low']), 2),
                'previous_close': round(float(previous['Close']), 2),
                'change': round(float(change), 2),
                'change_percent': round(float(change_pct), 2),
                'volume': int(latest.get('Volume', 0)),
                'market_cap': info.get('marketCap', 'N/A'),
                'currency': info.get('currency', 'USD'),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting latest price for {ticker}: {e}")
            raise
    
    def get_stock_info(self, ticker: str) -> Dict[str, Any]:
        """
        Get detailed stock information.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with stock information
        """
        try:
            ticker = ticker.upper().strip()
            stock = yf.Ticker(ticker)
            info = stock.info
            
            return {
                'ticker': ticker,
                'name': info.get('shortName', ticker),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'market_cap': info.get('marketCap', 'N/A'),
                'pe_ratio': info.get('trailingPE', 'N/A'),
                'eps': info.get('trailingEps', 'N/A'),
                'dividend_yield': info.get('dividendYield', 'N/A'),
                'fifty_two_week_high': info.get('fiftyTwoWeekHigh', 'N/A'),
                'fifty_two_week_low': info.get('fiftyTwoWeekLow', 'N/A'),
                'avg_volume': info.get('averageVolume', 'N/A'),
                'beta': info.get('beta', 'N/A'),
                'currency': info.get('currency', 'USD'),
                'exchange': info.get('exchange', 'N/A')
            }
            
        except Exception as e:
            logger.error(f"Error getting stock info for {ticker}: {e}")
            raise
    
    def validate_ticker(self, ticker: str) -> Tuple[bool, str]:
        """
        Validate if a ticker symbol exists.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Tuple of (is_valid, message)
        """
        try:
            ticker = ticker.upper().strip()
            
            if not ticker or len(ticker) > 10:
                return False, "Invalid ticker format"
            
            stock = yf.Ticker(ticker)
            history = stock.history(period='5d')
            
            if history.empty:
                return False, f"No data found for ticker: {ticker}"
            
            return True, f"Valid ticker: {ticker}"
            
        except Exception as e:
            return False, f"Error validating ticker: {str(e)}"
    
    def search_tickers(self, query: str, limit: int = 10) -> List[Dict[str, str]]:
        """
        Search for stock tickers matching a query.
        
        Args:
            query: Search query
            limit: Maximum results to return
            
        Returns:
            List of matching tickers with names
        """
        query = query.upper().strip()
        
        # Simple search from popular tickers
        matches = [
            {'ticker': t, 'name': t}
            for t in self.POPULAR_TICKERS
            if query in t
        ][:limit]
        
        return matches
    
    def get_market_status(self) -> Dict[str, Any]:
        """
        Get current market status.
        
        Returns:
            Dictionary with market status info
        """
        now = datetime.now()
        
        # Simple market hours check (NYSE hours in EST)
        market_open = now.replace(hour=9, minute=30, second=0)
        market_close = now.replace(hour=16, minute=0, second=0)
        
        is_weekday = now.weekday() < 5
        is_market_hours = market_open <= now <= market_close
        
        return {
            'is_open': is_weekday and is_market_hours,
            'current_time': now.isoformat(),
            'market_open': '09:30 EST',
            'market_close': '16:00 EST',
            'day_of_week': now.strftime('%A')
        }
    
    def clear_cache(self):
        """Clear the data cache."""
        self._cache.clear()
        logger.info("Data cache cleared")
