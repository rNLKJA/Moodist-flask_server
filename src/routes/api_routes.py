"""API routes."""

from flask import jsonify

from src.controllers import api_controller
from src.routes import api


@api.route("/status")
def status():
    """API status endpoint."""
    return api_controller.status()


@api.route("/info")
def info():
    """API info endpoint."""
    return api_controller.info()
