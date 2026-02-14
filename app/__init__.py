"""
Flask Application Factory
=========================
Creates and configures the Flask application instance.
"""

import os
import logging
from flask import Flask
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_app(config_name=None):
    """
    Application factory for creating Flask app instance.
    
    Args:
        config_name: Configuration environment name
        
    Returns:
        Configured Flask application instance
    """
    from app.config import get_config, Config
    
    # Create Flask app
    app = Flask(
        __name__,
        template_folder=str(Config.TEMPLATES_DIR),
        static_folder=str(Config.STATIC_DIR)
    )
    
    # Load configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    config_class = get_config()
    app.config.from_object(config_class)
    
    # Ensure required directories exist
    _ensure_directories(app)
    
    # Initialize extensions and services
    _init_extensions(app)
    
    # Register blueprints
    _register_blueprints(app)
    
    # Register error handlers
    _register_error_handlers(app)
    
    logger.info(f"Application initialized in {config_name} mode")
    
    return app


def _ensure_directories(app):
    """Ensure required directories exist."""
    from app.config import Config
    
    directories = [
        Config.REPORTS_DIR,
        Config.MODELS_DIR
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)


def _init_extensions(app):
    """Initialize Flask extensions and load ML models."""
    from services.forecasting_service import ForecastingService
    
    # Load ML model at startup to avoid reloading on each request
    with app.app_context():
        try:
            forecasting_service = ForecastingService()
            app.forecasting_service = forecasting_service
            logger.info("ML model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load ML model: {e}")
            app.forecasting_service = None


def _register_blueprints(app):
    """Register application blueprints."""
    from routes.main_routes import main_bp
    from routes.api_routes import api_bp
    from routes.forecast_routes import forecast_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(forecast_bp, url_prefix='/forecast')
    
    logger.info("Blueprints registered")


def _register_error_handlers(app):
    """Register error handlers."""
    from flask import jsonify, render_template
    
    @app.errorhandler(404)
    def not_found_error(error):
        if _is_api_request():
            return jsonify({'error': 'Resource not found'}), 404
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        if _is_api_request():
            return jsonify({'error': 'Internal server error'}), 500
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        logger.error(f"Unhandled exception: {error}")
        if _is_api_request():
            return jsonify({'error': str(error)}), 500
        return render_template('errors/500.html'), 500


def _is_api_request():
    """Check if current request is an API request."""
    from flask import request
    return request.path.startswith('/api/')
