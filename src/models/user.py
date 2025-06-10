"""User model for Flask-Login integration with CouchDB."""

from flask_login import UserMixin
from src.utils.couchdb_client import CouchDBClient
from src.utils.token_generator import verify_password
import logging

# Configure logger
logger = logging.getLogger(__name__)

class User(UserMixin):
    """User model for Flask-Login that works with CouchDB documents."""
    
    def __init__(self, user_data):
        """
        Initialize a User instance from a CouchDB document.
        
        Args:
            user_data (dict): User document from CouchDB
        """
        self.id = user_data.get('_id')
        self.email = user_data.get('email')
        self.user_type = user_data.get('user_type')
        self.is_verified = user_data.get('is_verified', False)
        self.status = user_data.get('status')
        self.unique_id = user_data.get('unique_id')
        self.created_at = user_data.get('created_at')
        self.updated_at = user_data.get('updated_at')
        self._user_data = user_data  # Store the full document
    
    def get_id(self):
        """Override to return the user's ID."""
        return self.id
    
    @property
    def is_active(self):
        """Return True if the user is active."""
        return self.is_verified and self.status in ['verified', 'active']
    
    @property
    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return True
    
    @property
    def is_anonymous(self):
        """Return False as anonymous users are not supported."""
        return False
    
    def get_db_name(self):
        """Get the appropriate database name based on user type."""
        database_mapping = {
            'patient': 'patient',
            'doctor': 'clinician', 
            'admin': 'moodist'
        }
        return database_mapping.get(self.user_type, 'moodist')
    
    def get_data(self):
        """Return the full user document."""
        return self._user_data
    
    @classmethod
    def get_by_id(cls, user_id):
        """
        Get a user by ID from the appropriate database.
        
        Args:
            user_id (str): User document ID
            
        Returns:
            User or None: User instance if found, None otherwise
        """
        try:
            # Try each database until we find the user
            client = CouchDBClient()
            databases = ['patient', 'clinician', 'moodist']
            
            for db_name in databases:
                try:
                    user_doc = client.get_document(db_name, user_id)
                    if user_doc:
                        return cls(user_doc)
                except Exception:
                    continue
            
            return None
        except Exception as e:
            logger.error(f"Error getting user by ID {user_id}: {str(e)}")
            return None
    
    @classmethod
    def get_by_email(cls, email, user_type=None):
        """
        Get a user by email from the appropriate database.
        
        Args:
            email (str): User email address
            user_type (str, optional): User type to limit search
            
        Returns:
            User or None: User instance if found, None otherwise
        """
        try:
            client = CouchDBClient()
            
            # If user_type is provided, only search that database
            if user_type:
                database_mapping = {
                    'patient': 'patient',
                    'doctor': 'clinician', 
                    'admin': 'moodist'
                }
                db_name = database_mapping.get(user_type, 'moodist')
                users = client.find_documents(db_name, {"email": email}, limit=1)
                if users:
                    return cls(users[0])
                return None
            
            # Otherwise, search all databases
            databases = ['patient', 'clinician', 'moodist']
            for db_name in databases:
                try:
                    users = client.find_documents(db_name, {"email": email}, limit=1)
                    if users:
                        return cls(users[0])
                except Exception:
                    continue
            
            return None
        except Exception as e:
            logger.error(f"Error getting user by email {email}: {str(e)}")
            return None
    
    @classmethod
    def authenticate(cls, email, password, user_type=None):
        """
        Authenticate a user by email and password.
        
        Args:
            email (str): User email address
            password (str): User password
            user_type (str, optional): User type to limit search
            
        Returns:
            dict: Authentication result with status and details
                - {'status': 'success', 'user': user} if authentication successful and user is verified
                - {'status': 'unverified', 'user': user} if password is correct but user is not verified
                - {'status': 'email_not_found'} if email not found
                - {'status': 'invalid_password'} if password is incorrect
        """
        user = cls.get_by_email(email, user_type)
        if not user:
            logger.warning(f"Authentication failed: User with email {email} not found")
            return {'status': 'email_not_found'}
        
        # First verify password
        stored_hash = user._user_data.get('password')
        if not stored_hash or not verify_password(stored_hash, password):
            logger.warning(f"Authentication failed: Invalid password for user {email}")
            return {'status': 'invalid_password'}
        
        # Password is correct, now check verification status
        if not user.is_verified:
            logger.warning(f"Authentication partial: User {email} password correct but not verified")
            return {'status': 'unverified', 'user': user}
        
        logger.info(f"User {email} authenticated successfully")
        return {'status': 'success', 'user': user} 