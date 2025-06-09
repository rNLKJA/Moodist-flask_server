"""Index routes."""

from flask import jsonify
from src.routes import index
from src.controllers import index_controller
 
@index.route('/')
def home():
    """Home page route."""
    return index_controller.index()