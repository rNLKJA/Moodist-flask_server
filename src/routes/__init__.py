"""Routes package."""

from flask import Blueprint

# Create blueprints
api = Blueprint('api', __name__, url_prefix='/api')
index = Blueprint('index', __name__)
system = Blueprint('system', __name__, url_prefix='/system')

# Import routes
from src.routes import index_routes, api_routes, system_routes
from src.routes.couch_test import couch_test
from src.routes.connection_test import connection_test
from src.routes.auth_routes import auth_bp

# Register routes with blueprints
# This is done in the import of the route modules

__all__ = ['api', 'index', 'system', 'couch_test', 'connection_test', 'auth_bp'] 