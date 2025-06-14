"""Mood logging controller."""

from flask import jsonify, request
from flask_login import current_user, login_required
import logging
from src.models.mood_log import MoodLog

# Configure logger
logger = logging.getLogger(__name__)

@login_required
def check_today_log():
    """
    Check if the user has already logged their mood today.
    
    Returns:
        JSON response with has_logged_today status
    """
    try:
        # Get current user ID
        user_id = current_user.id
        
        # Check if user has logged today
        has_logged = MoodLog.has_logged_today(user_id)
        
        return jsonify({
            "success": True,
            "has_logged_today": has_logged
        })
        
    except Exception as e:
        logger.error(f"Error checking today's log: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Failed to check today's log",
            "details": str(e)
        }), 500

@login_required
def save_mood_scores():
    """
    Save mood scores for the current user.
    
    Expected request body:
    {
        "scores": {
            "q1": 0-3,
            "q2": 0-3,
            "q3": 0-3,
            "q4": 0-3,
            "q5": 0-3
        }
    }
    
    Returns:
        JSON response with success status
    """
    try:
        # Get current user ID
        user_id = current_user.id
        
        # Check if user has already logged today
        if MoodLog.has_logged_today(user_id):
            return jsonify({
                "success": False,
                "error": "You have already logged your mood today"
            }), 400
        
        # Get scores from request
        data = request.get_json()
        if not data or 'scores' not in data:
            return jsonify({
                "success": False,
                "error": "Missing scores in request"
            }), 400
            
        scores = data['scores']
        
        # Save mood log
        result = MoodLog.save_mood_log(user_id, scores)
        
        if result.get('success'):
            return jsonify({
                "success": True,
                "message": "Mood scores saved successfully",
                "id": result.get('id')
            })
        else:
            return jsonify({
                "success": False,
                "error": result.get('error', "Failed to save mood scores")
            }), 400
            
    except Exception as e:
        logger.error(f"Error saving mood scores: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Failed to save mood scores",
            "details": str(e)
        }), 500

@login_required
def get_user_logs():
    """
    Get mood logs for the current user.
    
    Returns:
        JSON response with user's mood logs
    """
    try:
        # Get current user ID
        user_id = current_user.id
        
        # Get limit from query parameters
        limit = request.args.get('limit', default=None, type=int)
        
        # Get user logs
        logs = MoodLog.get_user_logs(user_id, limit=limit)
        
        return jsonify({
            "success": True,
            "logs": logs
        })
        
    except Exception as e:
        logger.error(f"Error getting user logs: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Failed to get user logs",
            "details": str(e)
        }), 500 