"""Flask application package."""

from flask import Flask
from dotenv import load_dotenv
import os
from werkzeug.middleware.proxy_fix import ProxyFix

# Load environment variables from .env file if it exists
load_dotenv()

def create_app(config_name='default'):
    """Create Flask application using the application factory pattern.
    
    Args:
        config_name: The configuration to use
        
    Returns:
        Flask: The configured Flask application
    """
    app = Flask(__name__)
    
    # Load configuration
    from src.config import config as app_config
    app.config.from_object(app_config[config_name])
    
    # Configure ProxyFix for running behind a proxy in production
    if config_name == 'production' and app.config.get('PROXY_FIX', False):
        app.wsgi_app = ProxyFix(
            app.wsgi_app,
            x_for=app.config.get('PROXY_FIX_X_FOR', 1),
            x_proto=app.config.get('PROXY_FIX_X_PROTO', 1),
            x_host=app.config.get('PROXY_FIX_X_HOST', 1),
            x_port=app.config.get('PROXY_FIX_X_PORT', 1)
        )
    
    # Setup middleware
    from src.middleware import setup_cors, setup_error_handlers, setup_logger, setup_ssl
    setup_ssl(app)  # SSL should be first to handle redirects
    setup_cors(app)
    setup_error_handlers(app)
    setup_logger(app)
    
    # Register blueprints
    from src.routes import api, index, system
    app.register_blueprint(api)
    app.register_blueprint(index)
    app.register_blueprint(system)
    
    # Log application startup
    app.logger.info(f"Application {app.config.get('APP_NAME')} started in {config_name} mode")
    
    return app 