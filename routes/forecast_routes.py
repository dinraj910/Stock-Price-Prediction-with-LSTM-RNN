"""
Forecast Routes Module
======================
Specialized routes for forecast-related operations.
"""

import logging
from flask import Blueprint, jsonify, request, current_app

from services.data_service import DataService
from services.indicator_service import IndicatorService
from app.config import Config

logger = logging.getLogger(__name__)

forecast_bp = Blueprint('forecast', __name__)

# Initialize services
data_service = DataService()
indicator_service = IndicatorService()


@forecast_bp.route('/dashboard/<ticker>', methods=['GET'])
def get_dashboard_data(ticker):
    """
    Get all data needed for the dashboard in one call.
    
    This combines multiple data fetches for efficiency.
    
    Query params:
        days: Historical days (default: 90)
        horizon: Forecast horizon (default: 5)
    """
    try:
        days = request.args.get('days', 90, type=int)
        horizon = request.args.get('horizon', 5, type=int)
        
        # Validate inputs
        days = max(30, min(days, 365))
        horizon = max(1, min(horizon, Config.MAX_FORECAST_HORIZON))
        
        # Fetch historical data
        historical_data = data_service.fetch_stock_data(ticker, period_days=days + 60)
        
        # Get latest price
        latest_price = data_service.get_latest_price(ticker)
        
        # Calculate indicators
        data_with_indicators = indicator_service.calculate_all_indicators(historical_data)
        chart_data = indicator_service.get_chart_data(data_with_indicators, days=days)
        
        # Get indicator summaries
        trend = indicator_service.get_trend_signal(data_with_indicators)
        volatility = indicator_service.get_volatility_metrics(data_with_indicators)
        rsi = indicator_service.get_rsi_signal(data_with_indicators)
        support_resistance = indicator_service.get_support_resistance(data_with_indicators)
        
        # Generate forecast
        forecast = None
        prediction = None
        
        if current_app.forecasting_service:
            try:
                prediction = current_app.forecasting_service.predict_next_day(
                    ticker, data=historical_data
                )
                forecast = current_app.forecasting_service.forecast_multi_day(
                    ticker, horizon, data=historical_data
                )
            except Exception as e:
                logger.warning(f"Forecast error: {e}")
        
        return jsonify({
            'success': True,
            'ticker': ticker.upper(),
            'latest': latest_price,
            'chart_data': chart_data,
            'indicators': {
                'trend': trend,
                'volatility': volatility,
                'rsi': rsi,
                'support_resistance': support_resistance
            },
            'prediction': prediction,
            'forecast': forecast,
            'disclaimer': Config.DISCLAIMER
        })
        
    except Exception as e:
        logger.error(f"Error fetching dashboard data: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@forecast_bp.route('/quick/<ticker>', methods=['GET'])
def get_quick_forecast(ticker):
    """
    Get a quick forecast summary for a ticker.
    
    Query params:
        horizon: Forecast horizon (default: 5)
    """
    try:
        horizon = request.args.get('horizon', 5, type=int)
        horizon = max(1, min(horizon, 7))  # Quick forecast limited to 7 days
        
        if not current_app.forecasting_service:
            return jsonify({
                'success': False,
                'error': 'Model not loaded'
            }), 500
        
        # Get latest price
        latest = data_service.get_latest_price(ticker)
        
        # Generate forecast
        forecast = current_app.forecasting_service.forecast_multi_day(ticker, horizon)
        
        # Quick summary
        summary = {
            'ticker': ticker.upper(),
            'current_price': latest['current_price'],
            'predicted_close': forecast['summary']['final_predicted_close'],
            'change': forecast['summary']['total_change'],
            'change_percent': forecast['summary']['total_change_percent'],
            'trend': forecast['summary']['trend'],
            'horizon': horizon
        }
        
        return jsonify({
            'success': True,
            **summary
        })
        
    except Exception as e:
        logger.error(f"Error in quick forecast: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@forecast_bp.route('/compare', methods=['POST'])
def compare_forecasts():
    """
    Compare forecasts for multiple tickers.
    
    JSON body:
        tickers: List of ticker symbols
        horizon: Forecast horizon (default: 5)
    """
    try:
        data = request.get_json()
        tickers = data.get('tickers', [])
        horizon = data.get('horizon', 5)
        
        if not tickers or len(tickers) > 5:
            return jsonify({
                'success': False,
                'error': 'Provide 1-5 tickers'
            }), 400
        
        if not current_app.forecasting_service:
            return jsonify({
                'success': False,
                'error': 'Model not loaded'
            }), 500
        
        results = []
        
        for ticker in tickers:
            try:
                forecast = current_app.forecasting_service.forecast_multi_day(ticker, horizon)
                latest = data_service.get_latest_price(ticker)
                
                results.append({
                    'ticker': ticker.upper(),
                    'current_price': latest['current_price'],
                    'predicted_close': forecast['summary']['final_predicted_close'],
                    'change_percent': forecast['summary']['total_change_percent'],
                    'trend': forecast['summary']['trend'],
                    'success': True
                })
            except Exception as e:
                results.append({
                    'ticker': ticker.upper(),
                    'success': False,
                    'error': str(e)
                })
        
        return jsonify({
            'success': True,
            'horizon': horizon,
            'comparison': results
        })
        
    except Exception as e:
        logger.error(f"Error comparing forecasts: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@forecast_bp.route('/analysis/<ticker>', methods=['GET'])
def get_full_analysis(ticker):
    """
    Get comprehensive analysis for a ticker.
    
    Query params:
        days: Historical days for analysis (default: 180)
    """
    try:
        days = request.args.get('days', 180, type=int)
        
        # Fetch data
        historical_data = data_service.fetch_stock_data(ticker, period_days=days + 60)
        
        # Get stock info
        stock_info = data_service.get_stock_info(ticker)
        
        # Calculate all indicators
        data_with_indicators = indicator_service.calculate_all_indicators(historical_data)
        
        # Get all indicator summaries
        trend = indicator_service.get_trend_signal(data_with_indicators)
        volatility = indicator_service.get_volatility_metrics(data_with_indicators)
        returns_stats = indicator_service.get_returns_statistics(data_with_indicators)
        support_resistance = indicator_service.get_support_resistance(data_with_indicators)
        rsi = indicator_service.get_rsi_signal(data_with_indicators)
        
        # Get model metrics if available
        model_metrics = None
        forecast = None
        
        if current_app.forecasting_service:
            try:
                model_metrics = current_app.forecasting_service.calculate_metrics(ticker)
                forecast = current_app.forecasting_service.forecast_multi_day(ticker, 5)
            except Exception as e:
                logger.warning(f"Analysis forecast error: {e}")
        
        return jsonify({
            'success': True,
            'ticker': ticker.upper(),
            'stock_info': stock_info,
            'technical_analysis': {
                'trend': trend,
                'rsi': rsi,
                'support_resistance': support_resistance
            },
            'risk_analysis': {
                'volatility': volatility,
                'returns': returns_stats
            },
            'model_performance': model_metrics,
            'forecast': forecast,
            'disclaimer': Config.DISCLAIMER
        })
        
    except Exception as e:
        logger.error(f"Error in full analysis: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
