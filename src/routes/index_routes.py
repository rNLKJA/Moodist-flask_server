"""Index routes."""

from flask import jsonify

from src.controllers import index_controller
from src.routes import index


@index.route("/")
def home():
    """Home page route."""
    return index_controller.index()
