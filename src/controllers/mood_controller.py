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
                "id": result.get('id'),
                "total_score": result.get('total_score')
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
    
    For patients: Returns simplified data with just date and total score
    For clinicians: Returns detailed data in table format
    
    Returns:
        JSON response with user's mood logs in appropriate format
    """
    try:
        # Get current user ID and type
        user_id = current_user.id
        user_type = current_user.user_type
        
        # Get limit from query parameters
        limit = request.args.get('limit', default=None, type=int)
        
        # Get user logs
        logs = MoodLog.get_user_logs(user_id, limit=limit)
        
        # Format logs based on user type
        if user_type == 'patient':
            # Simplified format for patients
            simplified_logs = []
            for log in logs:
                simplified_logs.append({
                    "log_date": log.get("log_date"),
                    "total_score": log.get("total_score")
                })
            
            return jsonify({
                "success": True,
                "logs": simplified_logs
            })
        elif user_type in ['doctor', 'admin']:
            # Table format for clinicians and admins
            table_data = {
                "headers": ["Date", "Q1", "Q2", "Q3", "Q4", "Q5", "Total"],
                "rows": []
            }
            
            for log in logs:
                scores = log.get("scores", {})
                row = [
                    log.get("log_date"),
                    scores.get("q1", "-"),
                    scores.get("q2", "-"),
                    scores.get("q3", "-"),
                    scores.get("q4", "-"),
                    scores.get("q5", "-"),
                    log.get("total_score", "-")
                ]
                table_data["rows"].append(row)
            
            return jsonify({
                "success": True,
                "table_data": table_data,
                "raw_logs": logs  # Include raw logs for advanced processing if needed
            })
        else:
            # Default format for unknown user types
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

@login_required
def get_recent_days_logs():
    """
    Get mood logs for the current user for recent days.
    
    Query parameters:
        days (int): Number of days to look back (default: 7)
    
    Returns:
        JSON response with user's mood logs for recent days
    """
    try:
        # Get current user ID and type
        user_id = current_user.id
        user_type = current_user.user_type
        
        # Get number of days from query parameters
        days = request.args.get('days', default=7, type=int)
        
        # Limit days to a reasonable range (1-30)
        days = max(1, min(days, 30))
        
        # Get recent logs
        logs_by_date = MoodLog.get_recent_days_logs(user_id, days=days)
        
        # Format response based on user type
        if user_type == 'patient':
            # Simplified format for patients
            simplified_data = []
            
            for date, log in logs_by_date.items():
                entry = {
                    "date": date,
                    "has_log": log is not None,
                    "total_score": log.get("total_score") if log else None
                }
                simplified_data.append(entry)
            
            # Sort by date (most recent first)
            simplified_data.sort(key=lambda x: x["date"], reverse=True)
            
            return jsonify({
                "success": True,
                "days": days,
                "logs": simplified_data
            })
        elif user_type in ['doctor', 'admin']:
            # Table format for clinicians and admins
            table_data = {
                "headers": ["Date", "Q1", "Q2", "Q3", "Q4", "Q5", "Total", "Logged"],
                "rows": []
            }
            
            # Sort dates in descending order
            sorted_dates = sorted(logs_by_date.keys(), reverse=True)
            
            for date in sorted_dates:
                log = logs_by_date[date]
                
                if log:
                    scores = log.get("scores", {})
                    row = [
                        date,
                        scores.get("q1", "-"),
                        scores.get("q2", "-"),
                        scores.get("q3", "-"),
                        scores.get("q4", "-"),
                        scores.get("q5", "-"),
                        log.get("total_score", "-"),
                        "Yes"
                    ]
                else:
                    row = [date, "-", "-", "-", "-", "-", "-", "No"]
                
                table_data["rows"].append(row)
            
            return jsonify({
                "success": True,
                "days": days,
                "table_data": table_data,
                "raw_data": logs_by_date  # Include raw data for advanced processing if needed
            })
        else:
            # Default format for unknown user types
            return jsonify({
                "success": True,
                "days": days,
                "logs_by_date": logs_by_date
            })
        
    except Exception as e:
        logger.error(f"Error getting recent logs: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Failed to get recent logs",
            "details": str(e)
        }), 500

@login_required
def get_patient_logs(patient_id):
    """
    Get mood logs for a specific patient (for clinicians only).
    
    Args:
        patient_id (str): Patient ID to get logs for
    
    Returns:
        JSON response with patient's mood logs in table format
    """
    try:
        # Check if user is authorized (doctor or admin)
        if current_user.user_type not in ['doctor', 'admin']:
            return jsonify({
                "success": False,
                "error": "Unauthorized access"
            }), 403
        
        # Get query parameters
        limit = request.args.get('limit', default=None, type=int)
        start_date = request.args.get('start_date', default=None, type=str)
        end_date = request.args.get('end_date', default=None, type=str)
        
        # Set up date range if provided
        date_range = None
        if start_date and end_date:
            date_range = {
                'start_date': start_date,
                'end_date': end_date
            }
        
        # Get patient logs
        logs = MoodLog.get_patient_logs(patient_id, date_range=date_range, limit=limit)
        
        # Format logs as table data
        table_data = {
            "headers": ["Date", "Q1", "Q2", "Q3", "Q4", "Q5", "Total"],
            "rows": []
        }
        
        for log in logs:
            scores = log.get("scores", {})
            row = [
                log.get("log_date"),
                scores.get("q1", "-"),
                scores.get("q2", "-"),
                scores.get("q3", "-"),
                scores.get("q4", "-"),
                scores.get("q5", "-"),
                log.get("total_score", "-")
            ]
            table_data["rows"].append(row)
        
        # Prepare summary data
        summary = {
            "total_entries": len(logs),
            "date_range": {
                "start": logs[-1].get("log_date") if logs else None,
                "end": logs[0].get("log_date") if logs else None
            },
            "average_score": sum(log.get("total_score", 0) for log in logs) / len(logs) if logs else 0
        }
        
        return jsonify({
            "success": True,
            "patient_id": patient_id,
            "table_data": table_data,
            "summary": summary,
            "raw_logs": logs  # Include raw logs for advanced processing if needed
        })
        
    except Exception as e:
        logger.error(f"Error getting logs for patient {patient_id}: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Failed to get logs for patient {patient_id}",
            "details": str(e)
        }), 500 