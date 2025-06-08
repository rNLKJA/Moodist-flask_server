"""CORS middleware."""

from flask_cors import CORS

def setup_cors(app):
    """Set up CORS for the application."""
    CORS(app, resources={r"/api/*": {"origins": "*"}}) 