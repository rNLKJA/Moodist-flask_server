"""SSL middleware for HTTP to HTTPS redirection."""

from flask import request, redirect, current_app

def setup_ssl(app):
    """Set up SSL middleware for the application.
    
    This middleware will:
    1. Redirect HTTP requests to HTTPS if SSL_REDIRECT is enabled
    2. Set HSTS headers to enforce HTTPS in browsers
    """
    
    @app.before_request
    def before_request():
        """Redirect HTTP requests to HTTPS if SSL_REDIRECT is enabled."""
        if app.config.get('SSL_REDIRECT', False):
            # Check if we're already on HTTPS
            if request.scheme == 'http':
                url = request.url.replace('http://', 'https://', 1)
                return redirect(url, code=301)  # Permanent redirect
    
    @app.after_request
    def add_security_headers(response):
        """Add security headers to all responses."""
        if app.config.get('SSL_ENABLED', False):
            # HTTP Strict Transport Security (HSTS)
            # This tells browsers to always use HTTPS
            if app.config.get('ENV') == 'production':
                # 1 year for production
                response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
            else:
                # Shorter time for development (1 hour)
                response.headers['Strict-Transport-Security'] = 'max-age=3600'
            
            # Content-Security-Policy
            response.headers['Content-Security-Policy'] = "default-src 'self'"
            
            # X-Content-Type-Options
            response.headers['X-Content-Type-Options'] = 'nosniff'
            
            # X-Frame-Options
            response.headers['X-Frame-Options'] = 'SAMEORIGIN'
            
        return response 