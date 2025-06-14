"""Mood logging routes."""

from flask import Blueprint
from src.controllers import mood_controller

# Create blueprint
mood_bp = Blueprint('mood', __name__, url_prefix='/api/mood')

# Define routes
@mood_bp.route('/check-today', methods=['GET'])
def check_today_log():
    """Check if user has logged mood today."""
    return mood_controller.check_today_log()

@mood_bp.route('/log', methods=['POST'])
def save_mood_scores():
    """Save mood scores."""
    return mood_controller.save_mood_scores()

@mood_bp.route('/logs', methods=['GET'])
def get_user_logs():
    """Get user mood logs."""
    return mood_controller.get_user_logs() 