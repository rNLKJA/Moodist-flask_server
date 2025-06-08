"""Routes package."""

from flask import Blueprint

# Create blueprints
api = Blueprint('api', __name__, url_prefix='/api')
index = Blueprint('index', __name__)

# Import routes
from src.routes import index_routes, api_routes

# Register routes with blueprints
# This is done in the import of the route modules

__all__ = ['api', 'index'] 