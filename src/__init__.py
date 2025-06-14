"""Flask application package."""

from flask import Flask
from dotenv import load_dotenv
import os
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_login import LoginManager
from flask_session import Session

# Load environment variables from .env file if it exists
load_dotenv()

# Initialize extensions
login_manager = LoginManager()
session = Session()

@login_manager.user_loader
def load_user(user_id):
    """Load a user from the database by ID."""
    from src.models.user import User
    return User.get_by_id(user_id)

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
    
    # Initialize extensions
    login_manager.init_app(app)
    session.init_app(app)
    
    # Configure login manager
    login_manager.session_protection = "strong"
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "info"
    
    # Setup middleware
    from src.middleware import setup_cors, setup_error_handlers, setup_logger, setup_ssl
    setup_ssl(app)  # SSL should be first to handle redirects
    setup_cors(app)
    setup_error_handlers(app)
    setup_logger(app)
    
    # Register blueprints
    from src.routes import api, index, system, couch_test, connection_test, auth_bp, mood_bp
    app.register_blueprint(api)
    app.register_blueprint(index)
    app.register_blueprint(system)
    app.register_blueprint(couch_test)
    app.register_blueprint(connection_test)
    app.register_blueprint(auth_bp)
    app.register_blueprint(mood_bp)
    
    # Log application startup
    app.logger.info(f"Application {app.config.get('APP_NAME')} started in {config_name} mode")
    
    return app 