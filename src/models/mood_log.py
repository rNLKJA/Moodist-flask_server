"""Mood log model for storing user mood scores."""

from datetime import datetime, timedelta
import pytz
import logging
from src.utils.couchdb_client import CouchDBClient

# Configure logger
logger = logging.getLogger(__name__)

class MoodLog:
    """Model for storing and retrieving user mood logs."""
    
    DB_NAME = "mood_logs"  # Separate database for mood logs
    
    @classmethod
    def has_logged_today(cls, user_id):
        """
        Check if the user has already logged their mood today (Melbourne time).
        
        Args:
            user_id (str): User ID to check
            
        Returns:
            bool: True if user has already logged today, False otherwise
        """
        try:
            # Get Melbourne timezone
            melbourne_tz = pytz.timezone('Australia/Melbourne')
            
            # Get current date in Melbourne time
            now = datetime.now(melbourne_tz)
            today_date = now.strftime('%Y-%m-%d')
            
            # Query for logs from today
            client = CouchDBClient()
            selector = {
                "user_id": user_id,
                "log_date": today_date
            }
            
            logs = client.find_documents(cls.DB_NAME, selector)
            
            # Return True if any logs found for today
            return len(logs) > 0
            
        except Exception as e:
            logger.error(f"Error checking if user {user_id} has logged today: {str(e)}")
            # In case of error, return False to allow logging
            return False
    
    @classmethod
    def save_mood_log(cls, user_id, scores):
        """
        Save mood scores for a user.
        
        Args:
            user_id (str): User ID
            scores (dict): Dictionary with keys 'q1' to 'q5' and values 0-3
            
        Returns:
            dict: Result of the save operation
        """
        try:
            # Validate scores
            if not isinstance(scores, dict):
                raise ValueError("Scores must be a dictionary")
                
            # Ensure all required questions are answered
            total_score = 0
            for q in range(1, 6):
                q_key = f"q{q}"
                if q_key not in scores:
                    raise ValueError(f"Missing score for question {q}")
                
                # Validate score range
                if not isinstance(scores[q_key], int) or scores[q_key] < 0 or scores[q_key] > 3:
                    raise ValueError(f"Score for question {q} must be an integer between 0 and 3")
                
                # Add to total score
                total_score += scores[q_key]
            
            # Get Melbourne timezone
            melbourne_tz = pytz.timezone('Australia/Melbourne')
            
            # Get current date and time in Melbourne time
            now = datetime.now(melbourne_tz)
            today_date = now.strftime('%Y-%m-%d')
            
            # Create mood log document
            mood_log = {
                "user_id": user_id,
                "log_date": today_date,
                "timestamp": now.isoformat(),
                "scores": scores,
                "total_score": total_score,
                "type": "mood_log"
            }
            
            # Save to database
            client = CouchDBClient()
            result = client.create_document(mood_log, cls.DB_NAME)
            
            if result:
                logger.info(f"Saved mood log for user {user_id} on {today_date} with total score {total_score}")
                return {"success": True, "id": result.get('id'), "total_score": total_score}
            else:
                logger.error(f"Failed to save mood log for user {user_id}")
                return {"success": False, "error": "Failed to save mood log"}
                
        except ValueError as e:
            logger.error(f"Validation error saving mood log for user {user_id}: {str(e)}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"Error saving mood log for user {user_id}: {str(e)}")
            return {"success": False, "error": "An unexpected error occurred"}
    
    @classmethod
    def get_user_logs(cls, user_id, limit=None):
        """
        Get mood logs for a user.
        
        Args:
            user_id (str): User ID
            limit (int, optional): Maximum number of logs to return
            
        Returns:
            list: List of mood logs
        """
        try:
            client = CouchDBClient()
            selector = {
                "user_id": user_id,
                "type": "mood_log"
            }
            
            logs = client.find_documents(cls.DB_NAME, selector, limit=limit)
            
            # Sort logs by date (most recent first)
            logs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            return logs
            
        except Exception as e:
            logger.error(f"Error getting mood logs for user {user_id}: {str(e)}")
            return []
    
    @classmethod
    def get_recent_days_logs(cls, user_id, days=7):
        """
        Get mood logs for a user for the most recent N days.
        
        Args:
            user_id (str): User ID
            days (int): Number of days to look back (default: 7)
            
        Returns:
            dict: Dictionary with dates as keys and log data as values
        """
        try:
            # Get Melbourne timezone
            melbourne_tz = pytz.timezone('Australia/Melbourne')
            
            # Get current date in Melbourne time
            now = datetime.now(melbourne_tz)
            
            # Calculate the date range (past N days including today)
            date_range = []
            for i in range(days):
                day = now - timedelta(days=i)
                date_range.append(day.strftime('%Y-%m-%d'))
            
            # Get all logs for this user
            client = CouchDBClient()
            selector = {
                "user_id": user_id,
                "type": "mood_log"
            }
            
            all_logs = client.find_documents(cls.DB_NAME, selector)
            
            # Filter logs to only include those in the date range
            filtered_logs = [log for log in all_logs if log.get('log_date') in date_range]
            
            # Create a dictionary with dates as keys and logs as values
            result = {}
            
            # Initialize with all dates in range having None value
            for date in date_range:
                result[date] = None
            
            # Fill in actual log data where available
            for log in filtered_logs:
                log_date = log.get('log_date')
                if log_date in result:
                    result[log_date] = log
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting recent logs for user {user_id}: {str(e)}")
            return {}
            
    @classmethod
    def get_patient_logs(cls, patient_id, date_range=None, limit=None):
        """
        Get mood logs for a specific patient (for clinicians).
        
        Args:
            patient_id (str): Patient user ID
            date_range (dict, optional): Dictionary with 'start_date' and 'end_date' keys
            limit (int, optional): Maximum number of logs to return
            
        Returns:
            list: List of mood logs
        """
        try:
            client = CouchDBClient()
            selector = {
                "user_id": patient_id,
                "type": "mood_log"
            }
            
            # Apply date range filter if provided
            if date_range and isinstance(date_range, dict):
                start_date = date_range.get('start_date')
                end_date = date_range.get('end_date')
                
                if start_date and end_date:
                    # Filter logs within date range
                    all_logs = client.find_documents(cls.DB_NAME, selector)
                    filtered_logs = [
                        log for log in all_logs 
                        if start_date <= log.get('log_date', '') <= end_date
                    ]
                    
                    # Sort logs by date (most recent first)
                    filtered_logs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
                    
                    # Apply limit if specified
                    if limit and len(filtered_logs) > limit:
                        return filtered_logs[:limit]
                    return filtered_logs
            
            # If no date range or invalid date range, get all logs
            logs = client.find_documents(cls.DB_NAME, selector, limit=limit)
            
            # Sort logs by date (most recent first)
            logs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            return logs
            
        except Exception as e:
            logger.error(f"Error getting mood logs for patient {patient_id}: {str(e)}")
            return [] 