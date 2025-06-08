"""Logger middleware."""

import logging
from flask import request, g
import time

def setup_logger(app):
    """Set up request logger for the application."""
    
    @app.before_request
    def before_request():
        """Log before request and store start time."""
        g.start_time = time.time()
        app.logger.info(f"Request: {request.method} {request.path}")
    
    @app.after_request
    def after_request(response):
        """Log after request with response time."""
        diff = time.time() - g.start_time
        app.logger.info(f"Response: {response.status} - {diff:.4f}s")
        return response 