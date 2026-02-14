"""
API Routes Module
=================
REST API endpoints for the stock forecast dashboard.
"""

import logging
from flask import Blueprint, jsonify, request, current_app, send_file

from services.data_service import DataService
from services.indicator_service import IndicatorService
from services.report_service import ReportService
from app.config import Config

logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__)

# Initialize services
data_service = DataService()
indicator_service = IndicatorService()
report_service = ReportService()


@api_bp.route('/stock/<ticker>', methods=['GET'])
def get_stock_data(ticker):
    """
    Get historical stock data with indicators.
    
    Query params:
        days: Number of days of historical data (default: 365)
    """
    try:
        days = request.args.get('days', 365, type=int)
        days = max(30, min(days, 365 * 5))  # Limit range
        
        # Fetch data
        data = data_service.fetch_stock_data(ticker, period_days=days)
        
        # Calculate indicators
        chart_data = indicator_service.get_chart_data(data, days=days)
        
        return jsonify({
            'success': True,
            'ticker': ticker.upper(),
            'data': chart_data
        })
        
    except Exception as e:
        logger.error(f"Error fetching stock data: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@api_bp.route('/stock/<ticker>/latest', methods=['GET'])
def get_latest_price(ticker):
    """Get the latest price information for a stock."""
    try:
        price_info = data_service.get_latest_price(ticker)
        
        return jsonify({
            'success': True,
            **price_info
        })
        
    except Exception as e:
        logger.error(f"Error getting latest price: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@api_bp.route('/stock/<ticker>/info', methods=['GET'])
def get_stock_info(ticker):
    """Get detailed stock information."""
    try:
        info = data_service.get_stock_info(ticker)
        
        return jsonify({
            'success': True,
            **info
        })
        
    except Exception as e:
        logger.error(f"Error getting stock info: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@api_bp.route('/stock/<ticker>/indicators', methods=['GET'])
def get_indicators(ticker):
    """
    Get technical indicators for a stock.
    
    Query params:
        days: Number of days of data to use (default: 100)
    """
    try:
        days = request.args.get('days', 100, type=int)
        
        # Fetch data
        data = data_service.fetch_stock_data(ticker, period_days=days + 60)
        
        # Calculate indicators
        data_with_indicators = indicator_service.calculate_all_indicators(data)
        
        # Get various indicator summaries
        trend = indicator_service.get_trend_signal(data_with_indicators)
        volatility = indicator_service.get_volatility_metrics(data_with_indicators)
        returns_stats = indicator_service.get_returns_statistics(data_with_indicators)
        support_resistance = indicator_service.get_support_resistance(data_with_indicators)
        rsi = indicator_service.get_rsi_signal(data_with_indicators)
        
        return jsonify({
            'success': True,
            'ticker': ticker.upper(),
            'trend': trend,
            'volatility': volatility,
            'returns': returns_stats,
            'support_resistance': support_resistance,
            'rsi': rsi
        })
        
    except Exception as e:
        logger.error(f"Error calculating indicators: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@api_bp.route('/predict', methods=['POST'])
def predict():
    """
    Make a single-day prediction.
    
    JSON body:
        ticker: Stock ticker symbol
    """
    try:
        data = request.get_json()
        ticker = data.get('ticker', Config.DEFAULT_TICKER)
        
        if not current_app.forecasting_service:
            return jsonify({
                'success': False,
                'error': 'Model not loaded'
            }), 500
        
        # Make prediction
        result = current_app.forecasting_service.predict_next_day(ticker)
        
        return jsonify({
            'success': True,
            **result
        })
        
    except Exception as e:
        logger.error(f"Error making prediction: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@api_bp.route('/forecast', methods=['POST'])
def forecast():
    """
    Generate multi-day forecast.
    
    JSON body:
        ticker: Stock ticker symbol
        horizon: Number of days to forecast (1-30)
    """
    try:
        data = request.get_json()
        ticker = data.get('ticker', Config.DEFAULT_TICKER)
        horizon = data.get('horizon', Config.DEFAULT_FORECAST_HORIZON)
        
        # Validate horizon
        horizon = max(1, min(int(horizon), Config.MAX_FORECAST_HORIZON))
        
        if not current_app.forecasting_service:
            return jsonify({
                'success': False,
                'error': 'Model not loaded'
            }), 500
        
        # Generate forecast
        result = current_app.forecasting_service.forecast_multi_day(ticker, horizon)
        
        return jsonify({
            'success': True,
            **result
        })
        
    except Exception as e:
        logger.error(f"Error generating forecast: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@api_bp.route('/metrics/<ticker>', methods=['GET'])
def get_metrics(ticker):
    """Get model performance metrics for a ticker."""
    try:
        if not current_app.forecasting_service:
            return jsonify({
                'success': False,
                'error': 'Model not loaded'
            }), 500
        
        # Calculate metrics
        result = current_app.forecasting_service.calculate_metrics(ticker)
        
        return jsonify({
            'success': True,
            **result
        })
        
    except Exception as e:
        logger.error(f"Error calculating metrics: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@api_bp.route('/model/info', methods=['GET'])
def get_model_info():
    """Get information about the loaded model."""
    try:
        if not current_app.forecasting_service:
            return jsonify({
                'success': False,
                'error': 'Model not loaded'
            }), 500
        
        info = current_app.forecasting_service.get_model_info()
        
        return jsonify({
            'success': True,
            **info
        })
        
    except Exception as e:
        logger.error(f"Error getting model info: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@api_bp.route('/validate/<ticker>', methods=['GET'])
def validate_ticker(ticker):
    """Validate if a ticker symbol exists."""
    try:
        is_valid, message = data_service.validate_ticker(ticker)
        
        return jsonify({
            'success': True,
            'valid': is_valid,
            'message': message
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@api_bp.route('/search', methods=['GET'])
def search_tickers():
    """
    Search for stock tickers.
    
    Query params:
        q: Search query
        limit: Maximum results (default: 10)
    """
    try:
        query = request.args.get('q', '')
        limit = request.args.get('limit', 10, type=int)
        
        results = data_service.search_tickers(query, limit)
        
        return jsonify({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@api_bp.route('/download/csv', methods=['POST'])
def download_csv():
    """
    Download forecast as CSV.
    
    JSON body:
        ticker: Stock ticker symbol
        horizon: Forecast horizon
    """
    try:
        data = request.get_json()
        ticker = data.get('ticker', Config.DEFAULT_TICKER)
        horizon = data.get('horizon', Config.DEFAULT_FORECAST_HORIZON)
        
        if not current_app.forecasting_service:
            return jsonify({
                'success': False,
                'error': 'Model not loaded'
            }), 500
        
        # Generate forecast
        forecast_data = current_app.forecasting_service.forecast_multi_day(ticker, horizon)
        
        # Generate CSV
        csv_buffer = report_service.generate_forecast_csv(forecast_data)
        
        filename = report_service.get_report_filename(ticker, 'csv')
        
        return send_file(
            csv_buffer,
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        logger.error(f"Error generating CSV: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@api_bp.route('/download/report', methods=['POST'])
def download_report():
    """
    Download full analysis report as CSV.
    
    JSON body:
        ticker: Stock ticker symbol
        horizon: Forecast horizon
    """
    try:
        req_data = request.get_json()
        ticker = req_data.get('ticker', Config.DEFAULT_TICKER)
        horizon = req_data.get('horizon', Config.DEFAULT_FORECAST_HORIZON)
        
        if not current_app.forecasting_service:
            return jsonify({
                'success': False,
                'error': 'Model not loaded'
            }), 500
        
        # Fetch data
        historical_data = data_service.fetch_stock_data(ticker, period_days=365)
        
        # Generate forecast
        forecast_data = current_app.forecasting_service.forecast_multi_day(ticker, horizon)
        
        # Get indicators
        data_with_indicators = indicator_service.calculate_all_indicators(historical_data)
        indicators = {
            'trend': indicator_service.get_trend_signal(data_with_indicators),
            'volatility': indicator_service.get_volatility_metrics(data_with_indicators),
            'returns': indicator_service.get_returns_statistics(data_with_indicators)
        }
        
        # Generate report
        csv_buffer = report_service.generate_csv_report(
            ticker, forecast_data, historical_data, indicators
        )
        
        filename = report_service.get_report_filename(ticker, 'csv')
        
        return send_file(
            csv_buffer,
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@api_bp.route('/market/status', methods=['GET'])
def market_status():
    """Get current market status."""
    try:
        status = data_service.get_market_status()
        
        return jsonify({
            'success': True,
            **status
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
