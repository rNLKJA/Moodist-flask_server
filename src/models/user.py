"""User model for CouchDB with improved status management."""

import uuid
from datetime import datetime
from src.utils.token_generator import hash_password

class User:
    """User model for CouchDB with improved status management."""
    
    def __init__(self, email, password=None, user_type="patient", first_name=None, 
                 last_name=None, is_verified=False, is_active=False, unique_id=None, 
                 status="pending_verification"):
        """
        Initialize a new user with improved status management.
        
        Args:
            email (str): User's email address
            password (str): User's password (will be hashed)
            user_type (str): Type of user (patient, doctor, admin)
            first_name (str): User's first name
            last_name (str): User's last name
            is_verified (bool): Whether the user's email is verified
            is_active (bool): Whether the user is active
            unique_id (str): Unique 6-character uppercase ID for the user
            status (str): User status (pending_verification, verified, inactive, suspended)
        """
        self.email = email.lower()
        self.user_type = user_type
        self.first_name = first_name
        self.last_name = last_name
        self.is_verified = is_verified
        self.is_active = is_active
        self.status = status
        self.created_at = datetime.utcnow().isoformat()
        self.updated_at = self.created_at
        self.verified_at = None
        self.unique_id = unique_id
        
        # Set password if provided
        if password:
            hashed_password = hash_password(password)
            if hashed_password:
                self.password = hashed_password
            else:
                raise ValueError("Failed to hash password")
        
        # Generate a unique ID for CouchDB
        self._id = f"user:{self.email}"
    
    def to_dict(self):
        """
        Convert user object to dictionary for CouchDB storage.
        
        Returns:
            dict: User data as dictionary
        """
        user_dict = {
            "_id": self._id,
            "type": "user",
            "user_type": self.user_type,
            "email": self.email,
            "password": getattr(self, 'password', None),
            "first_name": self.first_name,
            "last_name": self.last_name,
            "is_verified": self.is_verified,
            "is_active": self.is_active,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "verified_at": self.verified_at
        }
        
        # Add unique_id if it exists
        if self.unique_id:
            user_dict["unique_id"] = self.unique_id
        
        return user_dict
    
    @classmethod
    def from_dict(cls, data):
        """
        Create a user object from a dictionary.
        
        Args:
            data (dict): User data from CouchDB
            
        Returns:
            User: User object
        """
        user = cls(
            email=data.get('email'),
            user_type=data.get('user_type', 'patient'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            is_verified=data.get('is_verified', False),
            is_active=data.get('is_active', False),
            unique_id=data.get('unique_id'),
            status=data.get('status', 'pending_verification')
        )
        
        # Set attributes that aren't in the constructor
        user._id = data.get('_id')
        user.password = data.get('password')
        user.created_at = data.get('created_at')
        user.updated_at = data.get('updated_at')
        user.verified_at = data.get('verified_at')
        
        return user
    
    def verify_account(self, unique_id=None):
        """
        Mark the user account as verified and active.
        
        Args:
            unique_id (str): Unique ID to assign to the user
        """
        self.is_verified = True
        self.is_active = True
        self.status = "verified"
        self.verified_at = datetime.utcnow().isoformat()
        self.updated_at = datetime.utcnow().isoformat()
        
        if unique_id:
            self.unique_id = unique_id
    
    def is_pending_verification(self):
        """
        Check if the user is pending email verification.
        
        Returns:
            bool: True if pending verification, False otherwise
        """
        return self.status == "pending_verification" and not self.is_verified
    
    def can_resend_verification(self):
        """
        Check if verification can be resent for this user.
        
        Returns:
            bool: True if verification can be resent, False otherwise
        """
        return self.status in ["pending_verification"] and not self.is_verified
    
    def update_password(self, new_password):
        """
        Update the user's password.
        
        Args:
            new_password (str): New password to set
            
        Returns:
            bool: True if password was updated successfully, False otherwise
        """
        hashed_password = hash_password(new_password)
        if hashed_password:
            self.password = hashed_password
            self.updated_at = datetime.utcnow().isoformat()
            return True
        return False
    
    def get_display_name(self):
        """
        Get the user's display name.
        
        Returns:
            str: Display name for the user
        """
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        else:
            return self.email 