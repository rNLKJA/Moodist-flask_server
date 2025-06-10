"""Token generator for authentication codes and password hashing."""

import os
import time
import logging
import secrets
from datetime import datetime, timedelta
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, HashingError
import string

# Configure logger
logger = logging.getLogger(__name__)

# Initialize Argon2 password hasher with secure settings
password_hasher = PasswordHasher(
    time_cost=3,     # Number of iterations
    memory_cost=65536,  # Memory usage in kibibytes (64 MB)
    parallelism=4,   # Number of parallel threads
    hash_len=32,     # Length of the hash in bytes
    salt_len=16      # Length of the salt in bytes
)

def generate_verification_code(length=6):
    """
    Generate a cryptographically secure 6-digit verification code.
    
    Uses Python's secrets module for cryptographically secure random generation
    as recommended in modern security practices.
    
    Args:
        length (int): Length of the verification code (default: 6)
        
    Returns:
        str: Secure 6-digit numeric verification code
    """
    # Generate a cryptographically secure 6-digit code
    # Using secrets.choice for each digit ensures uniform distribution
    return ''.join(secrets.choice('0123456789') for _ in range(length))

def hash_password(password):
    """
    Hash a password using Argon2id with pepper (modern best practice).
    
    Argon2id is the recommended password hashing algorithm as of 2024.
    It provides resistance against both side-channel and GPU-based attacks.
    
    Args:
        password (str): Plain text password
        
    Returns:
        str: Hashed password using Argon2id
    """
    # Get pepper from environment variables (additional security layer)
    pepper = os.environ.get('SECURITY_PASSWORD_PEPPER', '')
    
    if not pepper:
        logger.warning("Password pepper not configured. Using less secure password hashing.")
    
    # Add pepper to the password (pepper is a secret value stored separately)
    peppered_password = password + pepper
    
    # Hash the password using Argon2id (includes salt automatically)
    try:
        hashed = password_hasher.hash(peppered_password)
        return hashed
    except Exception as e:
        logger.error(f"Password hashing failed: {str(e)}")
        return None

def verify_password(stored_hash, password):
    """
    Verify a password against a stored Argon2 hash.
    
    Args:
        stored_hash (str): Stored password hash
        password (str): Plain text password to verify
        
    Returns:
        bool: True if password matches, False otherwise
    """
    # Get pepper from environment variables
    pepper = os.environ.get('SECURITY_PASSWORD_PEPPER', '')
    
    # Add pepper to the password
    peppered_password = password + pepper
    
    # Verify the password using Argon2
    try:
        password_hasher.verify(stored_hash, peppered_password)
        return True
    except VerifyMismatchError:
        return False
    except Exception as e:
        logger.error(f"Password verification failed: {str(e)}")
        return False

def generate_verification_token(email, verification_code, expiration_days=7):
    """
    Generate a secure token for email verification with 7-day expiry.
    
    This token is used for verification links sent via email.
    
    Args:
        email (str): User's email address
        verification_code (str): 6-digit verification code
        expiration_days (int): Token expiration time in days (default: 7)
        
    Returns:
        str: Signed verification token
    """
    secret_key = os.environ.get('SECRET_KEY', '')
    salt = os.environ.get('SECURITY_PASSWORD_SALT', '')
    
    if not secret_key or not salt:
        logger.error("SECRET_KEY or SECURITY_PASSWORD_SALT not configured.")
        return None
    
    serializer = URLSafeTimedSerializer(secret_key)
    
    # Create a payload with email, verification code, and creation timestamp
    payload = {
        'email': email,
        'code': verification_code,
        'created_at': time.time(),
        'purpose': 'email_verification'
    }
    
    return serializer.dumps(payload, salt=salt)

def verify_verification_token(token, verification_code, expiration_days=7):
    """
    Verify a verification token and check if the verification code matches.
    
    Args:
        token (str): Token to verify
        verification_code (str): 6-digit verification code to check
        expiration_days (int): Token expiration time in days (default: 7)
        
    Returns:
        dict or None: Payload if token is valid and code matches, None otherwise
    """
    secret_key = os.environ.get('SECRET_KEY', '')
    salt = os.environ.get('SECURITY_PASSWORD_SALT', '')
    
    if not secret_key or not salt:
        logger.error("SECRET_KEY or SECURITY_PASSWORD_SALT not configured.")
        return None
    
    serializer = URLSafeTimedSerializer(secret_key)
    
    # Convert days to seconds for max_age parameter
    max_age_seconds = expiration_days * 24 * 60 * 60
    
    try:
        # Decode the token with 7-day expiration
        payload = serializer.loads(
            token,
            salt=salt,
            max_age=max_age_seconds
        )
        
        # Verify this is an email verification token
        if payload.get('purpose') != 'email_verification':
            logger.warning("Token purpose mismatch.")
            return None
        
        # Check if verification code matches
        if payload.get('code') == verification_code:
            return payload
        else:
            logger.warning("Verification code does not match.")
            return None
            
    except SignatureExpired:
        logger.warning("Verification token has expired (7 days).")
        return None
    except BadSignature:
        logger.warning("Verification token signature is invalid.")
        return None
    except Exception as e:
        logger.error(f"Error verifying verification token: {str(e)}")
        return None

# Legacy functions for backward compatibility
def generate_token(email, verification_code, expiration=None):
    """Legacy function - use generate_verification_token instead."""
    if expiration is None:
        # Default to 7 days for new workflow
        return generate_verification_token(email, verification_code, expiration_days=7)
    else:
        # Convert seconds to days for legacy support
        expiration_days = max(1, expiration // (24 * 60 * 60))
        return generate_verification_token(email, verification_code, expiration_days)

def verify_token(token, verification_code, expiration=None):
    """Legacy function - use verify_verification_token instead."""
    if expiration is None:
        return verify_verification_token(token, verification_code, expiration_days=7)
    else:
        # Convert seconds to days for legacy support
        expiration_days = max(1, expiration // (24 * 60 * 60))
        return verify_verification_token(token, verification_code, expiration_days)

def generate_verification_link_token(email, user_type='patient', expires_in_days=7):
    """
    Generate a secure token for email verification links.
    
    Args:
        email (str): User's email address
        user_type (str): Type of user (patient, doctor, admin)
        expires_in_days (int): Token expiration in days
        
    Returns:
        str: URL-safe token for verification links
    """
    try:
        secret_key = os.environ.get('SECRET_KEY')
        salt = os.environ.get('SECURITY_PASSWORD_SALT')
        
        if not secret_key or not salt:
            logger.error("SECRET_KEY or SECURITY_PASSWORD_SALT not set")
            return None
        
        serializer = URLSafeTimedSerializer(secret_key)
        
        # Create payload with email, user_type, and timestamp
        payload = {
            'email': email,
            'user_type': user_type,
            'created_at': datetime.utcnow().isoformat(),
            'expires_in_days': expires_in_days
        }
        
        token = serializer.dumps(payload, salt=salt)
        logger.info(f"Generated verification link token for email: {email}")
        return token
        
    except Exception as e:
        logger.error(f"Error generating verification link token: {str(e)}")
        return None

def verify_link_token(token, max_age_seconds=None):
    """
    Verify a verification link token and extract user information.
    
    Args:
        token (str): The token to verify
        max_age_seconds (int): Maximum age in seconds (defaults to 7 days)
        
    Returns:
        dict: User information if token is valid, None otherwise
    """
    try:
        secret_key = os.environ.get('SECRET_KEY')
        salt = os.environ.get('SECURITY_PASSWORD_SALT')
        
        if not secret_key or not salt:
            logger.error("SECRET_KEY or SECURITY_PASSWORD_SALT not set")
            return None
        
        # Default to 7 days if not specified
        if max_age_seconds is None:
            max_age_seconds = 7 * 24 * 60 * 60  # 7 days
        
        serializer = URLSafeTimedSerializer(secret_key)
        
        # Verify and extract payload
        payload = serializer.loads(token, salt=salt, max_age=max_age_seconds)
        
        logger.info(f"Successfully verified link token for email: {payload.get('email')}")
        return payload
        
    except SignatureExpired:
        logger.warning("Verification link token has expired")
        return None
    except BadSignature:
        logger.warning("Invalid verification link token signature")
        return None
    except Exception as e:
        logger.error(f"Error verifying link token: {str(e)}")
        return None

def generate_password_token(password, user_type='patient', expires_in_days=7):
    """
    Generate a secure token based on user password using Argon2id hashing.
    
    Args:
        password (str): User's plain text password
        user_type (str): Type of user (patient, doctor, admin)
        expires_in_days (int): Token expiration in days
        
    Returns:
        str: URL-safe token
    """
    try:
        secret_key = os.environ.get('SECRET_KEY')
        salt = os.environ.get('SECURITY_PASSWORD_SALT')
        pepper = os.environ.get('SECURITY_PASSWORD_PEPPER', '')
        
        if not secret_key or not salt:
            logger.error("SECRET_KEY or SECURITY_PASSWORD_SALT not set")
            return None
        
        # Add pepper to password for additional security
        seasoned_password = password + pepper
        
        # Hash the password using Argon2id
        password_hash = password_hasher.hash(seasoned_password)
        
        # Create a serializer
        serializer = URLSafeTimedSerializer(secret_key)
        
        # Create payload with password hash, user type, and expiration
        payload = {
            'password_hash': password_hash,
            'user_type': user_type,
            'created_at': datetime.utcnow().isoformat(),
            'expires_in_days': expires_in_days
        }
        
        token = serializer.dumps(payload, salt=salt)
        logger.info(f"Generated password token for user type: {user_type}")
        return token
        
    except HashingError as e:
        logger.error(f"Error hashing password: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error generating password token: {str(e)}")
        return None

def verify_password_token(token, password, max_age_seconds=None):
    """
    Verify a password token by checking the password against the stored hash.
    
    Args:
        token (str): The token to verify
        password (str): The password to verify against
        max_age_seconds (int): Maximum age in seconds (defaults to 7 days)
        
    Returns:
        dict: Token payload if verification succeeds, None otherwise
    """
    try:
        secret_key = os.environ.get('SECRET_KEY')
        salt = os.environ.get('SECURITY_PASSWORD_SALT')
        pepper = os.environ.get('SECURITY_PASSWORD_PEPPER', '')
        
        if not secret_key or not salt:
            logger.error("SECRET_KEY or SECURITY_PASSWORD_SALT not set")
            return None
        
        # Default to 7 days if not specified
        if max_age_seconds is None:
            max_age_seconds = 7 * 24 * 60 * 60  # 7 days
        
        serializer = URLSafeTimedSerializer(secret_key)
        
        # Verify and extract payload
        payload = serializer.loads(token, salt=salt, max_age=max_age_seconds)
        
        # Verify the password against the stored hash
        stored_hash = payload.get('password_hash')
        if not stored_hash:
            logger.error("No password hash found in token")
            return None
        
        # Add pepper to password for verification
        seasoned_password = password + pepper
        
        # Verify password using Argon2
        password_hasher.verify(stored_hash, seasoned_password)
        
        logger.info(f"Successfully verified password token for user type: {payload.get('user_type')}")
        return payload
        
    except VerifyMismatchError:
        logger.warning("Password verification failed - password does not match token")
        return None
    except SignatureExpired:
        logger.warning("Password token has expired")
        return None
    except BadSignature:
        logger.warning("Invalid password token signature")
        return None
    except Exception as e:
        logger.error(f"Error verifying password token: {str(e)}")
        return None

# Legacy function for SHA-256 (deprecated, use Argon2 functions above)
def generate_password_hash_legacy(password):
    """Generate SHA-256 hash of password (deprecated - use Argon2 functions)."""
    import hashlib
    logger.warning("Using deprecated SHA-256 password hashing - upgrade to Argon2")
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password_hash_legacy(password, hash_value):
    """Verify password against SHA-256 hash (deprecated - use Argon2 functions)."""
    logger.warning("Using deprecated SHA-256 password verification - upgrade to Argon2")
    return generate_password_hash_legacy(password) == hash_value 