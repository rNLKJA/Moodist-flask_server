"""API routes."""

from flask import jsonify
from src.routes import api
from src.controllers import api_controller

@api.route('/status')
def status():
    """API status endpoint."""
    return api_controller.status()

@api.route('/info')
def info():
    """API info endpoint."""
    return api_controller.info() 