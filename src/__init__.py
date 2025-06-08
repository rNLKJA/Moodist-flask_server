"""Flask application package."""

from flask import Flask
from dotenv import load_dotenv
import os

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
    
    # Setup middleware
    from src.middleware import setup_cors, setup_error_handlers, setup_logger, setup_ssl
    setup_ssl(app)  # SSL should be first to handle redirects
    setup_cors(app)
    setup_error_handlers(app)
    setup_logger(app)
    
    # Register blueprints
    from src.routes import api, index
    app.register_blueprint(api)
    app.register_blueprint(index)
    
    return app 