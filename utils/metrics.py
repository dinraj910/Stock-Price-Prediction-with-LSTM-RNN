"""
Financial and ML metrics calculation utilities.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Union


def calculate_mse(actual: np.ndarray, predicted: np.ndarray) -> float:
    """
    Calculate Mean Squared Error.
    
    Args:
        actual: Actual values
        predicted: Predicted values
        
    Returns:
        MSE value
    """
    return np.mean((actual - predicted) ** 2)


def calculate_rmse(actual: np.ndarray, predicted: np.ndarray) -> float:
    """
    Calculate Root Mean Squared Error.
    
    Args:
        actual: Actual values
        predicted: Predicted values
        
    Returns:
        RMSE value
    """
    return np.sqrt(calculate_mse(actual, predicted))


def calculate_mae(actual: np.ndarray, predicted: np.ndarray) -> float:
    """
    Calculate Mean Absolute Error.
    
    Args:
        actual: Actual values
        predicted: Predicted values
        
    Returns:
        MAE value
    """
    return np.mean(np.abs(actual - predicted))


def calculate_mape(actual: np.ndarray, predicted: np.ndarray, epsilon: float = 1e-8) -> float:
    """
    Calculate Mean Absolute Percentage Error.
    
    Args:
        actual: Actual values
        predicted: Predicted values
        epsilon: Small value to avoid division by zero
        
    Returns:
        MAPE value (as percentage)
    """
    return np.mean(np.abs((actual - predicted) / (actual + epsilon))) * 100


def calculate_r2(actual: np.ndarray, predicted: np.ndarray) -> float:
    """
    Calculate R-squared (coefficient of determination).
    
    Args:
        actual: Actual values
        predicted: Predicted values
        
    Returns:
        R² value
    """
    ss_res = np.sum((actual - predicted) ** 2)
    ss_tot = np.sum((actual - np.mean(actual)) ** 2)
    
    if ss_tot == 0:
        return 0.0
    
    return 1 - (ss_res / ss_tot)


def calculate_directional_accuracy(actual: np.ndarray, predicted: np.ndarray) -> float:
    """
    Calculate directional accuracy (percentage of correct direction predictions).
    
    Args:
        actual: Actual values (changes)
        predicted: Predicted values (changes)
        
    Returns:
        Directional accuracy (0-1)
    """
    if len(actual) < 2:
        return 0.0
    
    actual_direction = np.sign(np.diff(actual))
    predicted_direction = np.sign(np.diff(predicted))
    
    correct = np.sum(actual_direction == predicted_direction)
    return correct / len(actual_direction)


def calculate_sharpe_ratio(returns: np.ndarray, risk_free_rate: float = 0.02, periods_per_year: int = 252) -> float:
    """
    Calculate Sharpe Ratio.
    
    Args:
        returns: Array of returns
        risk_free_rate: Annual risk-free rate (default: 2%)
        periods_per_year: Number of trading periods per year
        
    Returns:
        Sharpe Ratio
    """
    if len(returns) == 0:
        return 0.0
    
    daily_rf = risk_free_rate / periods_per_year
    excess_returns = returns - daily_rf
    
    if np.std(excess_returns) == 0:
        return 0.0
    
    return np.sqrt(periods_per_year) * np.mean(excess_returns) / np.std(excess_returns)


def calculate_sortino_ratio(returns: np.ndarray, risk_free_rate: float = 0.02, periods_per_year: int = 252) -> float:
    """
    Calculate Sortino Ratio (uses downside deviation).
    
    Args:
        returns: Array of returns
        risk_free_rate: Annual risk-free rate
        periods_per_year: Number of trading periods per year
        
    Returns:
        Sortino Ratio
    """
    if len(returns) == 0:
        return 0.0
    
    daily_rf = risk_free_rate / periods_per_year
    excess_returns = returns - daily_rf
    
    downside_returns = excess_returns[excess_returns < 0]
    
    if len(downside_returns) == 0 or np.std(downside_returns) == 0:
        return 0.0
    
    downside_std = np.std(downside_returns)
    return np.sqrt(periods_per_year) * np.mean(excess_returns) / downside_std


def calculate_max_drawdown(prices: np.ndarray) -> Tuple[float, int, int]:
    """
    Calculate Maximum Drawdown.
    
    Args:
        prices: Array of prices
        
    Returns:
        Tuple of (max drawdown percentage, peak index, trough index)
    """
    if len(prices) == 0:
        return 0.0, 0, 0
    
    cummax = np.maximum.accumulate(prices)
    drawdown = (cummax - prices) / cummax
    
    max_dd_idx = np.argmax(drawdown)
    peak_idx = np.argmax(prices[:max_dd_idx + 1]) if max_dd_idx > 0 else 0
    
    return drawdown[max_dd_idx], peak_idx, max_dd_idx


def calculate_volatility(returns: np.ndarray, periods_per_year: int = 252) -> float:
    """
    Calculate annualized volatility.
    
    Args:
        returns: Array of returns
        periods_per_year: Number of trading periods per year
        
    Returns:
        Annualized volatility
    """
    if len(returns) == 0:
        return 0.0
    
    return np.std(returns) * np.sqrt(periods_per_year)


def calculate_beta(stock_returns: np.ndarray, market_returns: np.ndarray) -> float:
    """
    Calculate Beta (systematic risk).
    
    Args:
        stock_returns: Array of stock returns
        market_returns: Array of market returns
        
    Returns:
        Beta value
    """
    if len(stock_returns) != len(market_returns) or len(stock_returns) == 0:
        return 1.0
    
    covariance = np.cov(stock_returns, market_returns)[0, 1]
    market_variance = np.var(market_returns)
    
    if market_variance == 0:
        return 1.0
    
    return covariance / market_variance


def calculate_alpha(stock_returns: np.ndarray, market_returns: np.ndarray, 
                   risk_free_rate: float = 0.02, periods_per_year: int = 252) -> float:
    """
    Calculate Jensen's Alpha.
    
    Args:
        stock_returns: Array of stock returns
        market_returns: Array of market returns
        risk_free_rate: Annual risk-free rate
        periods_per_year: Number of trading periods per year
        
    Returns:
        Alpha value (annualized)
    """
    if len(stock_returns) != len(market_returns) or len(stock_returns) == 0:
        return 0.0
    
    beta = calculate_beta(stock_returns, market_returns)
    daily_rf = risk_free_rate / periods_per_year
    
    expected_return = np.mean(stock_returns) * periods_per_year
    market_return = np.mean(market_returns) * periods_per_year
    
    return expected_return - (risk_free_rate + beta * (market_return - risk_free_rate))


def calculate_information_ratio(returns: np.ndarray, benchmark_returns: np.ndarray, 
                                periods_per_year: int = 252) -> float:
    """
    Calculate Information Ratio.
    
    Args:
        returns: Portfolio returns
        benchmark_returns: Benchmark returns
        periods_per_year: Number of trading periods per year
        
    Returns:
        Information Ratio
    """
    if len(returns) != len(benchmark_returns) or len(returns) == 0:
        return 0.0
    
    active_returns = returns - benchmark_returns
    tracking_error = np.std(active_returns)
    
    if tracking_error == 0:
        return 0.0
    
    return np.sqrt(periods_per_year) * np.mean(active_returns) / tracking_error


def calculate_var(returns: np.ndarray, confidence_level: float = 0.95) -> float:
    """
    Calculate Value at Risk (VaR).
    
    Args:
        returns: Array of returns
        confidence_level: Confidence level (default: 95%)
        
    Returns:
        VaR value (as positive number representing potential loss)
    """
    if len(returns) == 0:
        return 0.0
    
    return -np.percentile(returns, (1 - confidence_level) * 100)


def calculate_cvar(returns: np.ndarray, confidence_level: float = 0.95) -> float:
    """
    Calculate Conditional Value at Risk (CVaR / Expected Shortfall).
    
    Args:
        returns: Array of returns
        confidence_level: Confidence level
        
    Returns:
        CVaR value
    """
    if len(returns) == 0:
        return 0.0
    
    var = calculate_var(returns, confidence_level)
    return -np.mean(returns[returns <= -var])


def calculate_calmar_ratio(returns: np.ndarray, prices: np.ndarray) -> float:
    """
    Calculate Calmar Ratio (annualized return / max drawdown).
    
    Args:
        returns: Array of returns
        prices: Array of prices
        
    Returns:
        Calmar Ratio
    """
    if len(returns) == 0 or len(prices) == 0:
        return 0.0
    
    annual_return = np.mean(returns) * 252
    max_dd, _, _ = calculate_max_drawdown(prices)
    
    if max_dd == 0:
        return 0.0
    
    return annual_return / max_dd


def calculate_all_metrics(actual: np.ndarray, predicted: np.ndarray) -> Dict[str, float]:
    """
    Calculate all prediction metrics.
    
    Args:
        actual: Actual values
        predicted: Predicted values
        
    Returns:
        Dictionary of all metrics
    """
    return {
        'mse': calculate_mse(actual, predicted),
        'rmse': calculate_rmse(actual, predicted),
        'mae': calculate_mae(actual, predicted),
        'mape': calculate_mape(actual, predicted),
        'r2': calculate_r2(actual, predicted),
        'directional_accuracy': calculate_directional_accuracy(actual, predicted)
    }


def calculate_all_risk_metrics(returns: np.ndarray, prices: np.ndarray, 
                               benchmark_returns: Optional[np.ndarray] = None) -> Dict[str, float]:
    """
    Calculate all risk-related metrics.
    
    Args:
        returns: Array of returns
        prices: Array of prices
        benchmark_returns: Optional benchmark returns for relative metrics
        
    Returns:
        Dictionary of all risk metrics
    """
    metrics = {
        'volatility': calculate_volatility(returns),
        'sharpe_ratio': calculate_sharpe_ratio(returns),
        'sortino_ratio': calculate_sortino_ratio(returns),
        'max_drawdown': calculate_max_drawdown(prices)[0],
        'var_95': calculate_var(returns, 0.95),
        'cvar_95': calculate_cvar(returns, 0.95),
        'calmar_ratio': calculate_calmar_ratio(returns, prices)
    }
    
    if benchmark_returns is not None and len(benchmark_returns) == len(returns):
        metrics['beta'] = calculate_beta(returns, benchmark_returns)
        metrics['alpha'] = calculate_alpha(returns, benchmark_returns)
        metrics['information_ratio'] = calculate_information_ratio(returns, benchmark_returns)
    
    return metrics
