"""Error handler middleware."""

from flask import jsonify

def setup_error_handlers(app):
    """Set up error handlers for the application."""
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors."""
        return jsonify({
            "error": "Not found",
            "message": str(error)
        }), 404
    
    @app.errorhandler(500)
    def server_error(error):
        """Handle 500 errors."""
        return jsonify({
            "error": "Internal server error",
            "message": str(error)
        }), 500 