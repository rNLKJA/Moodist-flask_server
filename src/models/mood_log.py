"""Mood log model for storing user mood scores."""

from datetime import datetime
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
            for q in range(1, 6):
                q_key = f"q{q}"
                if q_key not in scores:
                    raise ValueError(f"Missing score for question {q}")
                
                # Validate score range
                if not isinstance(scores[q_key], int) or scores[q_key] < 0 or scores[q_key] > 3:
                    raise ValueError(f"Score for question {q} must be an integer between 0 and 3")
            
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
                "type": "mood_log"
            }
            
            # Save to database
            client = CouchDBClient()
            result = client.create_document(mood_log, cls.DB_NAME)
            
            if result:
                logger.info(f"Saved mood log for user {user_id} on {today_date}")
                return {"success": True, "id": result.get('id')}
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