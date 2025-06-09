"""ID generator for unique user IDs with improved security and reliability."""

import secrets
import string
import logging

# Configure logger
logger = logging.getLogger(__name__)

def generate_unique_id(db, length=6, max_attempts=10):
    """
    Generate a unique uppercase ID for a user using cryptographically secure random generation.
    
    Args:
        db: CouchDB database instance
        length (int): Length of the ID (default: 6)
        max_attempts (int): Maximum number of attempts to generate a unique ID
        
    Returns:
        str: Unique uppercase ID or None if failed
    """
    if not db:
        logger.error("Database instance is None")
        return None
    
    for attempt in range(max_attempts):
        try:
            # Generate a cryptographically secure random uppercase ID
            unique_id = ''.join(secrets.choice(string.ascii_uppercase) for _ in range(length))
            
            # Check if the ID already exists in the database
            mapping_doc_id = f"user_id:{unique_id}"
            
            # Try to get the document - if it doesn't exist, we'll get an exception
            try:
                existing_doc = db[mapping_doc_id]
                logger.warning(f"Generated ID {unique_id} already exists, trying again (attempt {attempt+1}/{max_attempts})")
                continue
            except Exception:
                # Document doesn't exist, so this ID is unique
                logger.info(f"Generated unique ID: {unique_id}")
                return unique_id
                
        except Exception as e:
            logger.error(f"Error during ID generation attempt {attempt+1}: {str(e)}")
            continue
    
    # If we've reached this point, we couldn't generate a unique ID
    logger.error(f"Failed to generate a unique ID after {max_attempts} attempts")
    return None

def validate_unique_id(unique_id):
    """
    Validate that a unique ID meets the required format.
    
    Args:
        unique_id (str): The ID to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not unique_id:
        return False
    
    # Check if it's the right length and all uppercase letters
    if len(unique_id) != 6:
        return False
    
    if not unique_id.isupper():
        return False
    
    if not unique_id.isalpha():
        return False
    
    return True 