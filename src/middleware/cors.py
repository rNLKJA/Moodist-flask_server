"""CORS middleware."""

from flask_cors import CORS

def setup_cors(app):
    """Set up CORS for the application."""
    # Get CORS configuration from app config
    origins = app.config.get('CORS_ORIGINS', ['*'])
    supports_credentials = app.config.get('CORS_SUPPORTS_CREDENTIALS', True)
    allow_headers = app.config.get('CORS_ALLOW_HEADERS', ['Content-Type', 'Authorization'])
    methods = app.config.get('CORS_METHODS', ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'])
    
    # Configure CORS
    CORS(app, 
         resources={r"/*": {
             "origins": origins,
             "methods": methods,
             "allow_headers": allow_headers
         }}, 
         supports_credentials=supports_credentials) 