"""Verification model for CouchDB with 7-day expiry support."""

from datetime import datetime, timedelta
import uuid

class Verification:
    """Verification model for CouchDB with 7-day expiry support."""
    
    def __init__(self, email, code, token, expires_at=None, attempts=0, status="pending"):
        """
        Initialize a new verification with 7-day default expiry.
        
        Args:
            email (str): User's email address
            code (str): 6-digit verification code
            token (str): Secure verification token
            expires_at (str): Expiration time as ISO format string
            attempts (int): Number of verification attempts
            status (str): Verification status (pending, verified, expired, failed)
        """
        self.email = email.lower()
        self.code = code
        self.token = token
        self.attempts = attempts
        self.status = status
        self.created_at = datetime.utcnow().isoformat()
        
        # Set expiration time (default: 7 days from now for new workflow)
        if expires_at is None:
            self.expires_at = (datetime.utcnow() + timedelta(days=7)).isoformat()
        else:
            self.expires_at = expires_at
        
        # Generate a unique ID for CouchDB
        self._id = f"verification:{uuid.uuid4()}"
    
    def to_dict(self):
        """
        Convert verification object to dictionary for CouchDB storage.
        
        Returns:
            dict: Verification data as dictionary
        """
        return {
            "_id": self._id,
            "type": "verification",
            "email": self.email,
            "code": self.code,
            "token": self.token,
            "attempts": self.attempts,
            "status": self.status,
            "created_at": self.created_at,
            "expires_at": self.expires_at
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Create a verification object from a dictionary.
        
        Args:
            data (dict): Verification data from CouchDB
            
        Returns:
            Verification: Verification object
        """
        verification = cls(
            email=data.get('email'),
            code=data.get('code'),
            token=data.get('token'),
            expires_at=data.get('expires_at'),
            attempts=data.get('attempts', 0),
            status=data.get('status', 'pending')
        )
        
        # Set attributes that aren't in the constructor
        verification._id = data.get('_id')
        verification.created_at = data.get('created_at')
        
        return verification
    
    def is_expired(self):
        """
        Check if the verification has expired (7 days).
        
        Returns:
            bool: True if expired, False otherwise
        """
        try:
            expires_at = datetime.fromisoformat(self.expires_at.replace('Z', '+00:00'))
            return datetime.utcnow() > expires_at
        except ValueError:
            # Handle legacy date formats
            expires_at = datetime.fromisoformat(self.expires_at)
            return datetime.utcnow() > expires_at
    
    def increment_attempts(self):
        """
        Increment the number of verification attempts.
        Sets status to 'failed' if attempts exceed limit.
        """
        self.attempts += 1
        # Mark as failed after 5 attempts
        if self.attempts >= 5:
            self.status = 'failed'
    
    def mark_as_verified(self):
        """
        Mark the verification as successfully verified.
        """
        self.status = 'verified'
    
    def mark_as_expired(self):
        """
        Mark the verification as expired.
        """
        self.status = 'expired'
    
    def can_attempt_verification(self):
        """
        Check if verification attempts are still allowed.
        
        Returns:
            bool: True if attempts are allowed, False otherwise
        """
        return self.status == 'pending' and self.attempts < 5 and not self.is_expired()
    
    def get_time_remaining(self):
        """
        Get the time remaining until expiration.
        
        Returns:
            timedelta: Time remaining until expiration
        """
        try:
            expires_at = datetime.fromisoformat(self.expires_at.replace('Z', '+00:00'))
            remaining = expires_at - datetime.utcnow()
            return remaining if remaining.total_seconds() > 0 else timedelta(0)
        except ValueError:
            expires_at = datetime.fromisoformat(self.expires_at)
            remaining = expires_at - datetime.utcnow()
            return remaining if remaining.total_seconds() > 0 else timedelta(0) 