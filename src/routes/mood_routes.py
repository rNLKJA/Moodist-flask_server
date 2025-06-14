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

@mood_bp.route('/logs/recent', methods=['GET'])
def get_recent_days_logs():
    """Get user mood logs for recent days."""
    return mood_controller.get_recent_days_logs()

@mood_bp.route('/patient/<patient_id>/logs', methods=['GET'])
def get_patient_logs(patient_id):
    """Get logs for a specific patient (clinicians only)."""
    return mood_controller.get_patient_logs(patient_id) 