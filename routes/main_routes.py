"""
Main Routes Module
==================
Serves the main HTML templates for the dashboard.
"""

from flask import Blueprint, render_template, current_app

from app.config import Config

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Render the main dashboard page."""
    return render_template(
        'dashboard.html',
        title='Dashboard',
        default_ticker=Config.DEFAULT_TICKER,
        disclaimer=Config.DISCLAIMER
    )


@main_bp.route('/forecast')
def forecast():
    """Render the forecast page."""
    return render_template(
        'forecast.html',
        title='Price Forecast',
        default_ticker=Config.DEFAULT_TICKER,
        max_horizon=Config.MAX_FORECAST_HORIZON,
        disclaimer=Config.DISCLAIMER
    )


@main_bp.route('/report')
def report():
    """Render the report page."""
    return render_template(
        'report.html',
        title='Analysis Report',
        default_ticker=Config.DEFAULT_TICKER,
        disclaimer=Config.DISCLAIMER
    )


@main_bp.route('/health')
def health():
    """Health check endpoint."""
    model_status = 'loaded' if current_app.forecasting_service else 'not loaded'
    return {
        'status': 'healthy',
        'model': model_status,
        'version': Config.VERSION
    }
