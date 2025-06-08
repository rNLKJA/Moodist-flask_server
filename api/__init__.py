"""API package for Flask application."""

from flask import Blueprint

api_bp = Blueprint('api', __name__, url_prefix='/api')

# Import routes after creating the blueprint to avoid circular imports
from api.routes import index 