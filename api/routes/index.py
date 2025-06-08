"""API index routes."""

from flask import jsonify
from api import api_bp

@api_bp.route('/status')
def status():
    """Return API status."""
    return jsonify({
        "status": "running",
        "service": "flask_server"
    })

@api_bp.route('/info')
def info():
    """Return API information."""
    return jsonify({
        "name": "Flask Server API",
        "version": "1.0.0",
        "description": "A Flask server with HTTPS support"
    }) 