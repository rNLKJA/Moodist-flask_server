"""Middleware to add ngrok-skip-browser-warning header to all responses."""

from functools import wraps
from flask import Flask, make_response

def setup_ngrok_header(app: Flask):
    """Add ngrok-skip-browser-warning header to all responses.
    
    Args:
        app: Flask application instance
    """
    @app.after_request
    def add_ngrok_header(response):
        """Add ngrok-skip-browser-warning header to the response."""
        response.headers['ngrok-skip-browser-warning'] = 'true'
        return response
    
    app.logger.info("Ngrok skip browser warning header middleware configured") 