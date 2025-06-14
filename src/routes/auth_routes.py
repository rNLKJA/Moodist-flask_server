"""Authentication routes for user registration and verification."""

import logging
from datetime import datetime, timedelta
import os
from flask import Blueprint, request, jsonify, url_for, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from src.utils.couchdb_client import CouchDBClient
from src.utils.token_generator import (
    generate_verification_link_token, verify_link_token, hash_password, verify_password, generate_verification_code
)
from src.utils.email_sender import send_email
from src.models.user import User
import secrets
import time

# Configure logger
logger = logging.getLogger(__name__)

# Create blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

def get_database_name(user_type):
    """Get the appropriate database name based on user type."""
    database_mapping = {
        'patient': 'patient',
        'doctor': 'clinician', 
        'admin': 'moodist'
    }
    return database_mapping.get(user_type, 'moodist')

def find_user_by_email(email, user_type, client):
    """
    Find user by email in the appropriate database.
    
    Args:
        email (str): User's email address
        user_type (str): Type of user (patient, doctor, admin)
        client: CouchDB client instance
        
    Returns:
        dict or None: User document if found, None otherwise
    """
    db_name = get_database_name(user_type)
    
    try:
        # Search for user by email in the specific database
        users = client.find_documents(db_name, {"email": email}, limit=1)
        if users:
            return users[0]
        return None
    except Exception as e:
        logger.error(f"Error finding user by email {email} in {db_name}: {str(e)}")
        return None

def generate_unique_id(user_type, client):
    """
    Generate a unique 6-character uppercase ID for the user.
    Ensures the ID doesn't conflict with any existing _id or unique_id fields
    across all databases.
    """
    import string
    import secrets
    
    max_attempts = 50
    for attempt in range(max_attempts):
        # Generate 6-character uppercase ID
        unique_id = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        
        # Check if ID exists in any database (as _id or unique_id)
        databases_to_check = ['patient', 'clinician', 'moodist']
        id_exists = False
        
        for db in databases_to_check:
            try:
                # Check if document with this ID exists as _id
                try:
                    doc = client.get_document(db, unique_id)
                    if doc:
                        logger.info(f"ID {unique_id} already exists as _id in {db} database")
                        id_exists = True
                        break
                except Exception as e:
                    if "not_found" not in str(e):
                        logger.warning(f"Error checking _id in {db}: {str(e)}")
                
                # Check if any document has this as unique_id field
                result = client.find_documents(db, {"unique_id": unique_id}, limit=1)
                if result:
                    logger.info(f"ID {unique_id} already exists as unique_id in {db} database")
                    id_exists = True
                    break
                    
            except Exception as e:
                logger.warning(f"Could not check unique_id in database {db}: {str(e)}")
                continue
        
        if not id_exists:
            logger.info(f"Generated unique ID: {unique_id} for user type: {user_type}")
            return unique_id
            
    logger.error(f"Failed to generate unique ID after {max_attempts} attempts")
    return None

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Log in a user and create a session.
    
    Request body:
    {
        "email": "user@example.com",
        "password": "password123",
        "user_type": "patient" (optional)
    }
    
    Returns:
        JSON: Login status and user information
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'status': False,
                'message': 'No JSON data provided',
                'error_type': 'missing_data'
            }), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        user_type = data.get('user_type')  # Optional, will search all DBs if not provided
        
        if not email or not password:
            return jsonify({
                'status': False,
                'message': 'Email and password are required',
                'error_type': 'missing_credentials'
            }), 400
        
        # Authenticate user
        auth_result = User.authenticate(email, password, user_type)
        
        # Handle authentication based on status
        if auth_result['status'] == 'email_not_found':
            # Add a small delay to prevent timing attacks
            time.sleep(secrets.randbelow(100) / 1000)  # 0-100ms random delay
            return jsonify({
                'status': False,
                'message': 'No account found with this email address',
                'error_type': 'email_not_found'
            }), 401
        
        elif auth_result['status'] == 'invalid_password':
            # Add a small delay to prevent timing attacks
            time.sleep(secrets.randbelow(100) / 1000)  # 0-100ms random delay
            return jsonify({
                'status': False,
                'message': 'Incorrect password',
                'error_type': 'invalid_password'
            }), 401
        
        elif auth_result['status'] == 'unverified':
            user = auth_result['user']
            return jsonify({
                'status': False,
                'message': 'Please verify your email before logging in',
                'error_type': 'unverified_email',
                'email': user.email,
                'user_type': user.user_type
            }), 403
        
        # User is verified and password is correct
        user = auth_result['user']
        
        # Log in the user with Flask-Login
        login_user(user, remember=True)
        
        # Record login time and IP address
        client = CouchDBClient()
        db_name = user.get_db_name()
        user_data = user.get_data()
        
        # Update login history
        login_history = user_data.get('login_history', [])
        login_history.append({
            'timestamp': datetime.utcnow().isoformat(),
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', 'Unknown')
        })
        
        # Keep only the last 5 logins
        if len(login_history) > 5:
            login_history = login_history[-5:]
        
        user_data['login_history'] = login_history
        user_data['last_login'] = datetime.utcnow().isoformat()
        user_data['updated_at'] = datetime.utcnow().isoformat()
        
        # Save updated user data
        try:
            client.save_document(db_name, user_data)
        except Exception as e:
            logger.error(f"Failed to update login history: {str(e)}")
        
        # Return success response with user info
        return jsonify({
            'status': True,
            'message': 'Login successful',
            'user': {
                'email': user.email,
                'user_type': user.user_type,
                'unique_id': user.unique_id
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({
            'status': False,
            'message': 'An error occurred during login',
            'error_type': 'server_error'
        }), 500

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """
    Log out the current user and clear the session.
    
    Returns:
        JSON: Logout status
    """
    try:
        # Record logout time
        if current_user.is_authenticated:
            client = CouchDBClient()
            db_name = current_user.get_db_name()
            user_data = current_user.get_data()
            
            user_data['last_logout'] = datetime.utcnow().isoformat()
            user_data['updated_at'] = datetime.utcnow().isoformat()
            
            try:
                client.save_document(db_name, user_data)
            except Exception as e:
                logger.error(f"Failed to update logout time: {str(e)}")
        
        # Log out the user
        logout_user()
        
        # Clear the session
        session.clear()
        
        return jsonify({
            'status': True,
            'message': 'Logout successful'
        }), 200
        
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return jsonify({
            'status': False,
            'message': 'An error occurred during logout',
            'error_type': 'server_error'
        }), 500

@auth_bp.route('/session', methods=['GET'])
def check_session():
    """
    Check the current user's session status.
    
    Returns:
        JSON: Session status and user information if logged in
    """
    try:
        if current_user.is_authenticated:
            return jsonify({
                'status': True,
                'authenticated': True,
                'user': {
                    'email': current_user.email,
                    'user_type': current_user.user_type,
                    'unique_id': current_user.unique_id
                }
            }), 200
        else:
            return jsonify({
                'status': True,
                'authenticated': False
            }), 200
            
    except Exception as e:
        logger.error(f"Session check error: {str(e)}")
        return jsonify({
            'status': False,
            'message': 'An error occurred checking session',
            'authenticated': False,
            'error_type': 'server_error'
        }), 500

@auth_bp.route('/create-user/<user_type>', methods=['POST'])
def create_user(user_type):
    """
    Create a user and send verification link via email.
    Uses 6-character unique ID as document _id.
    """
    try:
        # Validate user type
        valid_user_types = ['patient', 'doctor', 'admin']
        if user_type not in valid_user_types:
            return jsonify({
                'status': 'error',
                'message': f'Invalid user type. Must be one of: {", ".join(valid_user_types)}'
            }), 400

        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No JSON data provided'
            }), 400

        # Extract and validate required fields
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')

        if not email or not password:
            return jsonify({
                'status': 'error',
                'message': 'Email and password are required'
            }), 400

        # Initialize CouchDB client
        client = CouchDBClient()
        
        # Check if user already exists by email
        existing_user = find_user_by_email(email, user_type, client)
        
        # Handle duplicate email registration
        if existing_user:
            if existing_user.get('status') in ['verified', 'active'] or existing_user.get('is_verified'):
                # User already verified - return status: false for frontend to redirect to reset password
                logger.info(f"User {email} already verified, returning status: false")
                return jsonify({
                    'status': False,
                    'message': 'Account already exists. Please use reset password.',
                    'redirect_to_reset': True
                }), 200
            else:
                # User exists but not verified - resend verification link
                logger.info(f"Resending verification link for existing unverified user: {email}")
        else:
            # Create new user
            logger.info(f"Creating new user: {email} of type: {user_type}")
        
        # Generate verification link token
        verification_token = generate_verification_link_token(email, user_type, expires_in_days=7)
        if not verification_token:
            return jsonify({
                'status': 'error',
                'message': 'Failed to generate verification token'
            }), 500

        # Hash the password
        password_hash = hash_password(password)
        if not password_hash:
            return jsonify({
                'status': 'error',
                'message': 'Failed to hash password'
            }), 500

        # Calculate expiration date (7 days from now)
        expires_at = datetime.utcnow() + timedelta(days=7)

        # Generate a unique 6-character ID for the user
        unique_id = None
        if existing_user:
            # Use existing ID if updating
            unique_id = existing_user['_id']
            logger.info(f"Using existing ID {unique_id} for user {email}")
        else:
            # Generate new 6-character ID for new users
            # The improved generate_unique_id function already checks for conflicts
            # with both _id and unique_id fields across all databases
            unique_id = generate_unique_id(user_type, client)
            if not unique_id:
                logger.error(f"Failed to generate unique ID for user {email}")
                return jsonify({
                    'status': 'error',
                    'message': 'Failed to generate unique ID'
                }), 500
            logger.info(f"Generated new ID {unique_id} for user {email}")

        # Create user object with 6-character ID
        user_data = {
            "_id": unique_id,  # Use 6-character ID as document _id
            'type': user_type,
            'user_type': user_type,
            'email': email,
            'password': password_hash,
            'is_verified': False,
            'status': 'pending_verification',
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
            'verification_token': verification_token,
            'token_expires_at': expires_at.isoformat(),
            'unique_id': unique_id  # Also store as a field for consistency
        }

        # If updating existing user, preserve document metadata
        if existing_user and '_rev' in existing_user:
            user_data['_rev'] = existing_user['_rev']

        # Save user to the appropriate database
        try:
            db_name = get_database_name(user_type)
            result = client.save_document(db_name, user_data)
            logger.info(f"Successfully saved user to {db_name} database: {result}")
            
        except Exception as e:
            logger.error(f"Failed to save user to {db_name} database: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': 'Failed to create user account'
            }), 500

        # Generate verification URL
        verification_url = f"https://{os.getenv('DOMAIN_NAME')}:20001/auth/verify-link/{verification_token}"
        
        # Send verification email
        email_subject = "Verify Your Moodist Account - Action Required (7 Days)"
        email_template = f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="padding: 30px;">
                    <h2 style="text-align: center; margin-bottom: 30px;">
                        Welcome to Moodist! 
                    </h2>
                    
                    <p style="font-size: 16px; line-height: 1.6;">
                        Hello,
                    </p>
                    
                    <p style="font-size: 16px; line-height: 1.6;">
                        Thank you for signing up for Moodist as an user. 
                        To complete your registration and activate your account, please click the verification link below:
                    </p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{verification_url}" 
                           style="padding: 15px 30px; text-decoration: none; border: 1px solid #000; 
                                  display: inline-block; font-size: 16px;">
                            Verify My Account
                        </a>
                    </div>
                    
                    <div style="border: 1px solid #000; padding: 15px; margin: 20px 0;">
                        <p style="margin: 0; font-weight: bold;">
                            Important: This verification link expires in 7 days
                        </p>
                        <p style="margin: 5px 0 0 0; font-size: 14px;">
                            If you don't verify your account within 7 days, you'll need to register again.
                        </p>
                    </div>
                    
                    <p style="font-size: 14px; margin-top: 30px;">
                        If the button doesn't work, you can copy and paste this link into your browser:
                        <br>
                        <span style="word-break: break-all; font-family: monospace; padding: 5px;">
                            {verification_url}
                        </span>
                    </p>
                    
                    <hr style="margin: 30px 0;">
                    
                    <p style="font-size: 14px; text-align: center;">
                        If you didn't create this account, please ignore this email.
                        <br><br>
                        Best regards,<br>
                        <strong>The Moodist Team</strong>
                    </p>
                </div>
            </body>
        </html>
        """

        email_sent = send_email(email, email_subject, email_template)
        
        if not email_sent:
            return jsonify({
                'status': 'error',
                'message': 'User created but failed to send verification email'
            }), 500

        logger.info(f"Successfully sent verification email to {email}")

        return jsonify({
            'status': True,
            'message': 'Verification link sent to your email',
            'token': verification_token,
            'expires_at': expires_at.isoformat(),
            'expires_in_days': 7
        }), 201

    except Exception as e:
        logger.error(f"Error in create_user: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500

@auth_bp.route('/verify-link/<token>', methods=['GET'])
def verify_link(token):
    """
    Verify user account via email link and activate the account.
    Generates 6-character unique_id as secondary identifier.
    """
    try:
        # Verify the token
        payload = verify_link_token(token)
        if not payload:
            return jsonify({
                'status': 'error',
                'message': 'Invalid or expired verification link'
            }), 400

        email = payload.get('email')
        user_type = payload.get('user_type')
        
        if not email or not user_type:
            return jsonify({
                'status': 'error',
                'message': 'Invalid token payload'
            }), 400

        # Initialize CouchDB client
        client = CouchDBClient()
        
        # Find the user by email
        user = find_user_by_email(email, user_type, client)
        if not user:
            return jsonify({
                'status': 'error',
                'message': 'User not found'
            }), 404
        
        # Check if user is already verified
        if user.get('status') in ['verified', 'active'] or user.get('is_verified'):
            return """
            <html>
                <head>
                    <style>
                        body {
                            display: flex;
                            flex-direction: column;
                            justify-content: center;
                            align-items: center;
                            min-height: 100vh;
                            margin: 0;
                            font-family: Arial, sans-serif;
                            background-color: #f8f9fa;
                        }
                        .container {
                            text-align: center;
                            padding: 2rem;
                            background-color: white;
                            border-radius: 8px;
                            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                            max-width: 600px;
                            width: 90%;
                        }
                        h1 { color: #2c3e50; margin-bottom: 1.5rem; }
                        p { color: #34495e; font-size: 18px; margin: 1rem 0; }
                        .footer { color: #7f8c8d; margin-top: 2rem; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>Email Already Verified</h1>
                        <p>Your account has already been verified.</p>
                        <p class="footer">University of Melbourne @ Moodist Team - 2025</p>
                    </div>
                </body>
            </html>
            """

        # Generate unique 6-character ID (secondary identifier)
        unique_id = generate_unique_id(user_type, client)
        if not unique_id:
            return jsonify({
                'status': 'error',
                'message': 'Failed to generate unique user ID'
            }), 500

        # Update user status
        user['status'] = 'verified'
        user['is_verified'] = True
        
        # If unique_id doesn't exist, set it to the document ID
        if 'unique_id' not in user:
            user['unique_id'] = user['_id']
            
        user['verified_at'] = datetime.utcnow().isoformat()
        user['updated_at'] = datetime.utcnow().isoformat()
        
        # Remove verification token (no longer needed)
        user.pop('verification_token', None)
        user.pop('token_expires_at', None)

        # Save updated user
        try:
            db_name = get_database_name(user_type)
            result = client.save_document(db_name, user)
            logger.info(f"Successfully verified user {email} with ID {unique_id}")
            
            # Return formatted HTML response
            return """
            <html>
                <head>
                    <style>
                        body {
                            display: flex;
                            flex-direction: column;
                            justify-content: center;
                            align-items: center;
                            min-height: 100vh;
                            margin: 0;
                            font-family: Arial, sans-serif;
                            background-color: #f8f9fa;
                        }
                        .container {
                            text-align: center;
                            padding: 2rem;
                            background-color: white;
                            border-radius: 8px;
                            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                            max-width: 600px;
                            width: 90%;
                        }
                        h1 { color: #2c3e50; margin-bottom: 1.5rem; }
                        p { color: #34495e; font-size: 18px; margin: 1rem 0; }
                        .success { color: #27ae60; font-size: 16px; }
                        .footer { color: #7f8c8d; margin-top: 2rem; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>Email Successfully Verified!</h1>
                        <p>Thank you for verifying your email address.</p>
                        <p class="success">Your account is now active.</p>
                        <p class="footer">University of Melbourne @ Moodist Team - 2025</p>
                    </div>
                </body>
            </html>
            """

        except Exception as e:
            logger.error(f"Failed to update user status: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': 'Failed to verify account'
            }), 500

    except Exception as e:
        logger.error(f"Error in verify_link: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500

@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """
    Change the password for the currently logged-in user.
    
    Request body:
    {
        "current_password": "current123",
        "new_password": "new123"
    }
    
    Returns:
        JSON: Password change status
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No JSON data provided'
            }), 400
        
        current_password = data.get('current_password', '')
        new_password = data.get('new_password', '')
        
        if not current_password or not new_password:
            return jsonify({
                'status': 'error',
                'message': 'Current password and new password are required'
            }), 400
        
        # Get user data
        user_data = current_user.get_data()
        stored_hash = user_data.get('password')
        
        # Verify current password
        if not verify_password(stored_hash, current_password):
            # Add a small delay to prevent timing attacks
            time.sleep(secrets.randbelow(100) / 1000)  # 0-100ms random delay
            return jsonify({
                'status': 'error',
                'message': 'Current password is incorrect'
            }), 401
        
        # Hash the new password
        new_password_hash = hash_password(new_password)
        if not new_password_hash:
            return jsonify({
                'status': 'error',
                'message': 'Failed to hash new password'
            }), 500
        
        # Update password in user data
        user_data['password'] = new_password_hash
        user_data['updated_at'] = datetime.utcnow().isoformat()
        user_data['password_changed_at'] = datetime.utcnow().isoformat()
        
        # Save updated user data
        client = CouchDBClient()
        db_name = current_user.get_db_name()
        
        try:
            client.save_document(db_name, user_data)
            logger.info(f"Password changed successfully for user {current_user.email}")
            
            return jsonify({
                'status': 'success',
                'message': 'Password changed successfully'
            }), 200
            
        except Exception as e:
            logger.error(f"Failed to save new password: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': 'Failed to save new password'
            }), 500
        
    except Exception as e:
        logger.error(f"Change password error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'An error occurred while changing password'
        }), 500

# Keep the old verify endpoint for backward compatibility if needed
@auth_bp.route('/verify', methods=['POST'])
def verify_user():
    """
    Legacy verification endpoint (deprecated - use verification links instead).
    """
    return jsonify({
        'status': 'error',
        'message': 'This endpoint is deprecated. Please use the verification link sent to your email.'
    }), 410

@auth_bp.route('/resend-verification', methods=['POST'])
def resend_verification():
    """
    Resend verification email to unverified users.
    
    Request body:
    {
        "email": "user@example.com",
        "user_type": "patient" (optional)
    }
    
    Returns:
        JSON: Status of the resend operation
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'status': False,
                'message': 'No JSON data provided',
                'error_type': 'missing_data'
            }), 400
        
        email = data.get('email', '').strip().lower()
        user_type = data.get('user_type')  # Optional, will search all DBs if not provided
        
        if not email:
            return jsonify({
                'status': False,
                'message': 'Email is required',
                'error_type': 'missing_email'
            }), 400
        
        # Find the user
        client = CouchDBClient()
        user_doc = None
        db_name = None
        
        if user_type:
            # If user_type is provided, only search that database
            db_name = get_database_name(user_type)
            user_doc = find_user_by_email(email, user_type, client)
        else:
            # Otherwise, search all databases
            databases = [('patient', 'patient'), ('doctor', 'clinician'), ('admin', 'moodist')]
            for user_type, database in databases:
                user_doc = find_user_by_email(email, user_type, client)
                if user_doc:
                    db_name = database
                    break
        
        if not user_doc:
            # Don't reveal if user exists or not for security
            return jsonify({
                'status': True,
                'message': 'If your email exists in our system and is not verified, a new verification link has been sent.'
            }), 200
        
        # Check if user is already verified
        if user_doc.get('status') in ['verified', 'active'] or user_doc.get('is_verified', False):
            return jsonify({
                'status': False,
                'message': 'Your email is already verified. Please log in.',
                'error_type': 'already_verified'
            }), 400
        
        # Generate a new verification token
        user_type = user_doc.get('user_type', 'patient')
        verification_token = generate_verification_link_token(email, user_type, expires_in_days=7)
        if not verification_token:
            return jsonify({
                'status': False,
                'message': 'Failed to generate verification token',
                'error_type': 'token_generation_failed'
            }), 500
        
        # Update the user document with the new token
        expires_at = datetime.utcnow() + timedelta(days=7)
        user_doc['verification_token'] = verification_token
        user_doc['token_expires_at'] = expires_at.isoformat()
        user_doc['updated_at'] = datetime.utcnow().isoformat()
        
        # Save the updated user document
        try:
            client.save_document(db_name, user_doc)
        except Exception as e:
            logger.error(f"Failed to update user with new verification token: {str(e)}")
            return jsonify({
                'status': False,
                'message': 'Failed to generate new verification link',
                'error_type': 'database_error'
            }), 500
        
        # Generate verification URL
        verification_url = f"https://{os.getenv('DOMAIN_NAME')}:20001/auth/verify-link/{verification_token}"
        
        # Send verification email
        email_subject = "Verify Your Moodist Account - Action Required (7 Days)"
        email_template = f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background-color: #f8f9fa; padding: 30px; border-radius: 10px;">
                    <h2 style="color: #2c3e50; text-align: center; margin-bottom: 30px;">
                        Moodist Account Verification
                    </h2>
                    
                    <p style="font-size: 16px; line-height: 1.6; color: #333333;">
                        Hello,
                    </p>
                    
                    <p style="font-size: 16px; line-height: 1.6; color: #34495e;">
                        You requested a new verification link for your Moodist account.
                        To complete your registration and activate your account, please click the verification link below:
                    </p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{verification_url}" 
                           style="background-color: #3498db; color: white; padding: 15px 30px; 
                                  text-decoration: none; border-radius: 5px; font-weight: bold; 
                                  display: inline-block; font-size: 16px;">
                            Verify My Account
                        </a>
                    </div>
                    
                    <div style="background-color: #f8f9fa; border: 1px solid #012169; padding: 15px; 
                               border-radius: 5px; margin: 20px 0;">
                        <p style="margin: 0; color: #012169; font-weight: bold;">
                            Important: This verification link expires in 7 days
                        </p>
                        <p style="margin: 5px 0 0 0; color: #856404; font-size: 14px;">
                            If you don't verify your account within 7 days, you'll need to register again.
                        </p>
                    </div>
                    
                    <p style="font-size: 14px; color: #7f8c8d; margin-top: 30px;">
                        If the button doesn't work, you can copy and paste this link into your browser:
                        <br>
                        <span style="word-break: break-all; font-family: monospace; background-color: #ecf0f1; padding: 5px;">
                            {verification_url}
                        </span>
                    </p>
                    
                    <hr style="border: none; border-top: 1px solid #bdc3c7; margin: 30px 0;">
                    
                    <p style="font-size: 14px; color: #7f8c8d; text-align: center;">
                        If you didn't request this verification link, please ignore this email.
                        <br><br>
                        Best regards,<br>
                        <strong>The Moodist Team</strong>
                    </p>
                </div>
            </body>
        </html>
        """
        
        email_sent = send_email(email, email_subject, email_template)
        
        if not email_sent:
            return jsonify({
                'status': False,
                'message': 'Failed to send verification email',
                'error_type': 'email_sending_failed'
            }), 500
        
        logger.info(f"Successfully resent verification email to {email}")
        
        return jsonify({
            'status': True,
            'message': 'Verification link has been sent to your email',
            'expires_in_days': 7
        }), 200
        
    except Exception as e:
        logger.error(f"Error in resend_verification: {str(e)}")
        return jsonify({
            'status': False,
            'message': 'An error occurred while resending verification',
            'error_type': 'server_error'
        }), 500

@auth_bp.route('/request-password-reset', methods=['POST'])
def request_password_reset():
    """
    Request a password reset code to be sent to the user's email.
    Input: { 
        "email": "user@example.com",
        "user_type": "patient" // Required: "patient", "doctor", or "admin"
    }
    """
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        user_type = data.get('user_type', 'patient')  # Default to patient if not specified
        
        if not email:
            return jsonify({ 'status': False, 'message': 'Email is required' }), 400
            
        if user_type not in ['patient', 'doctor', 'admin']:
            return jsonify({ 'status': False, 'message': 'Invalid user type' }), 400
        
        # Find user in specific database based on user_type
        client = CouchDBClient()
        db_name = get_database_name(user_type)
        user_doc = find_user_by_email(email, user_type, client)
        
        if not user_doc:
            # Don't reveal if user exists
            return jsonify({ 'status': True, 'message': 'If your email exists, a code has been sent.' }), 200
            
        # Generate code and expiration
        code = generate_verification_code(6)
        expires_at = datetime.utcnow() + timedelta(minutes=10)
        user_doc['password_reset_code'] = code
        user_doc['password_reset_expires_at'] = expires_at.isoformat()
        user_doc['updated_at'] = datetime.utcnow().isoformat()
        
        try:
            client.save_document(db_name, user_doc)
        except Exception as e:
            logger.error(f"Failed to save password reset code: {str(e)}")
            return jsonify({ 'status': False, 'message': 'Failed to process request' }), 500
            
        # Send plain text email
        email_subject = "Your Moodist Password Reset Code"
        email_body = f"""
You requested a password reset for your Moodist {user_type} account.

Your verification code is: {code}

This code will expire in 10 minutes.
If you did not request this, you can ignore this email.

University of Melbourne - Moodist Platform
"""
        email_sent = send_email(email, email_subject, email_body)
        if not email_sent:
            return jsonify({ 'status': False, 'message': 'Failed to send email' }), 500
            
        return jsonify({ 'status': True, 'message': 'If your email exists, a code has been sent.' }), 200
    except Exception as e:
        logger.error(f"Error in request_password_reset: {str(e)}")
        return jsonify({ 'status': False, 'message': 'Server error' }), 500

@auth_bp.route('/resend-password-reset-code', methods=['POST'])
def resend_password_reset_code():
    """
    Resend a new password reset code to the user's email.
    Input: { 
        "email": "user@example.com",
        "user_type": "patient" // Required: "patient", "doctor", or "admin"
    }
    """
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        user_type = data.get('user_type', 'patient')  # Default to patient if not specified
        
        if not email:
            return jsonify({ 'status': False, 'message': 'Email is required' }), 400
            
        if user_type not in ['patient', 'doctor', 'admin']:
            return jsonify({ 'status': False, 'message': 'Invalid user type' }), 400
        
        # Find user in specific database based on user_type
        client = CouchDBClient()
        db_name = get_database_name(user_type)
        user_doc = find_user_by_email(email, user_type, client)
        
        if not user_doc:
            return jsonify({ 'status': True, 'message': 'If your email exists, a code has been sent.' }), 200
            
        # Generate new code and expiration
        code = generate_verification_code(6)
        expires_at = datetime.utcnow() + timedelta(minutes=10)
        user_doc['password_reset_code'] = code
        user_doc['password_reset_expires_at'] = expires_at.isoformat()
        user_doc['updated_at'] = datetime.utcnow().isoformat()
        
        try:
            client.save_document(db_name, user_doc)
        except Exception as e:
            logger.error(f"Failed to save password reset code: {str(e)}")
            return jsonify({ 'status': False, 'message': 'Failed to process request' }), 500
            
        # Send plain text email
        email_subject = "Your Moodist Password Reset Code"
        email_body = f"""
You requested a password reset for your Moodist {user_type} account.

Your verification code is: {code}

This code will expire in 10 minutes.
If you did not request this, you can ignore this email.

University of Melbourne - Moodist Platform
"""
        email_sent = send_email(email, email_subject, email_body)
        if not email_sent:
            return jsonify({ 'status': False, 'message': 'Failed to send email' }), 500
            
        return jsonify({ 'status': True, 'message': 'If your email exists, a code has been sent.' }), 200
    except Exception as e:
        logger.error(f"Error in resend_password_reset_code: {str(e)}")
        return jsonify({ 'status': False, 'message': 'Server error' }), 500

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """
    Reset the user's password using the verification code.
    Input: { 
        "email": "user@example.com", 
        "password": "newPassword123", 
        "code": "123456",
        "user_type": "patient" // Required: "patient", "doctor", or "admin"
    }
    """
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        code = data.get('code', '').strip()
        user_type = data.get('user_type', 'patient')  # Default to patient if not specified
        
        if not email or not password or not code:
            return jsonify({ 'status': False, 'message': 'Email, password, and code are required' }), 400
            
        if user_type not in ['patient', 'doctor', 'admin']:
            return jsonify({ 'status': False, 'message': 'Invalid user type' }), 400
        
        # Find user in specific database based on user_type
        client = CouchDBClient()
        db_name = get_database_name(user_type)
        user_doc = find_user_by_email(email, user_type, client)
        
        if not user_doc:
            return jsonify({ 'status': False, 'message': 'Invalid email or code' }), 400
            
        # Check code and expiration
        stored_code = user_doc.get('password_reset_code')
        expires_at = user_doc.get('password_reset_expires_at')
        
        if not stored_code or not expires_at:
            return jsonify({ 'status': False, 'message': 'No reset code found' }), 400
            
        try:
            expires_at_dt = datetime.fromisoformat(expires_at)
        except Exception:
            return jsonify({ 'status': False, 'message': 'Invalid expiration format' }), 400
            
        if code != stored_code or datetime.utcnow() > expires_at_dt:
            return jsonify({ 'status': False, 'message': 'Invalid or expired code' }), 400
            
        # Update password
        password_hash = hash_password(password)
        if not password_hash:
            return jsonify({ 'status': False, 'message': 'Failed to hash password' }), 500
            
        user_doc['password'] = password_hash
        user_doc['updated_at'] = datetime.utcnow().isoformat()
        
        # Remove code
        user_doc.pop('password_reset_code', None)
        user_doc.pop('password_reset_expires_at', None)
        
        try:
            client.save_document(db_name, user_doc)
        except Exception as e:
            logger.error(f"Failed to update password: {str(e)}")
            return jsonify({ 'status': False, 'message': 'Failed to update password' }), 500
            
        return jsonify({ 'status': True, 'message': 'Password reset successful' }), 200
    except Exception as e:
        logger.error(f"Error in reset_password: {str(e)}")
        return jsonify({ 'status': False, 'message': 'Server error' }), 500

@auth_bp.route('/support', methods=['POST'])
def send_support_message():
    """
    Send an IT support message to the system maintainer.
    Can be used by both authenticated and non-authenticated users.
    
    Request body:
    {
        "message": "Detailed description of the issue",
        "user_type": "patient" (optional, only needed if not authenticated),
        "email": "user@example.com" (optional, only needed if not authenticated)
    }
    
    Returns:
        JSON: Status of the support request
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'status': False,
                'message': 'No JSON data provided',
                'error_type': 'missing_data'
            }), 400
        
        message = data.get('message', '').strip()
        if not message:
            return jsonify({
                'status': False,
                'message': 'Support message is required',
                'error_type': 'missing_message'
            }), 400
        
        # Get user details - either from session or from request body
        if current_user.is_authenticated:
            # User is logged in, get details from session
            user_type = current_user.user_type
            user_email = current_user.email
        else:
            # User is not logged in, get details from request body
            user_type = data.get('user_type', 'patient').lower()  # Default to patient
            user_email = data.get('email')
            
            # Email is required if not authenticated
            if not user_email:
                return jsonify({
                    'status': False,
                    'message': 'Email is required for support requests',
                    'error_type': 'missing_email'
                }), 400
        
        # Prepare email subject with user info for easy clustering
        email_subject = f"[Moodist Support] {user_type.capitalize()} - Support Request"
        
        # Prepare email body
        email_body = f"""
Support Request from Moodist User

User Type: {user_type}
User Email: {user_email}
Timestamp: {datetime.utcnow().isoformat()}

Message:
{message}

---
This is an automated message from the Moodist Platform.
"""
        
        # Send email to maintainer
        maintainer_email = os.getenv('SUPPORT_EMAIL', 'rinh@unimelb.edu.au')
        email_sent = send_email(maintainer_email, email_subject, email_body)
        
        if not email_sent:
            logger.error(f"Failed to send support email from user {user_email}")
            return jsonify({
                'status': False,
                'message': 'Failed to send support message',
                'error_type': 'email_failure'
            }), 500
        
        logger.info(f"Support message sent from user {user_email}")
        return jsonify({
            'status': True,
            'message': 'Support message sent successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error sending support message: {str(e)}")
        return jsonify({
            'status': False,
            'message': 'An error occurred while processing your support request',
            'error_type': 'server_error'
        }), 500

@auth_bp.route('/request-email-change', methods=['POST'])
@login_required
def request_email_change():
    """
    Request an email change by sending a verification code to the new email address.
    Requires authentication.
    
    Request body:
    {
        "new_email": "new_email@example.com"
    }
    
    Returns:
        JSON: Status of the request
    """
    try:
        # Log the request for debugging
        logger.info(f"Email change request received for user ID: {current_user.id}")
        
        data = request.get_json()
        if not data:
            logger.error("No JSON data provided in request body")
            return jsonify({
                'status': False,
                'message': 'No JSON data provided',
                'error_type': 'missing_data'
            }), 400
        
        # Log the received data
        logger.info(f"Email change request data: {data}")
        
        new_email = data.get('new_email', '').strip().lower()
        if not new_email:
            logger.error("New email is missing in request")
            return jsonify({
                'status': False,
                'message': 'New email is required',
                'error_type': 'missing_email'
            }), 400
            
        # Validate email format
        import re
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, new_email):
            logger.error(f"Invalid email format: {new_email}")
            return jsonify({
                'status': False,
                'message': 'Invalid email format',
                'error_type': 'invalid_email'
            }), 400
            
        # Get user data from the session
        client = CouchDBClient()
        db_name = current_user.get_db_name()
        user_id = current_user.id
        
        logger.info(f"Fetching user data from database: {db_name}, user ID: {user_id}")
        
        # Fetch the latest user data directly from the database
        try:
            user_data = client.get_document(db_name, user_id)
            if not user_data:
                logger.error(f"Could not find user document for ID {user_id} in database {db_name}")
                return jsonify({
                    'status': False,
                    'message': 'User data not found',
                    'error_type': 'user_not_found'
                }), 404
        except Exception as e:
            logger.error(f"Error fetching user data: {str(e)}")
            return jsonify({
                'status': False,
                'message': 'Error retrieving user data',
                'error_type': 'database_error'
            }), 500
            
        logger.info(f"User data retrieved successfully. Current email: {user_data.get('email')}")
            
        # Check if new email is different from current email
        current_email = user_data.get('email')
        if new_email == current_email:
            logger.error(f"New email {new_email} is the same as current email")
            return jsonify({
                'status': False,
                'message': 'New email must be different from current email',
                'error_type': 'same_email'
            }), 400
            
        # Check if the new email already exists in any database
        user_with_email = User.get_by_email(new_email)
        if user_with_email:
            logger.error(f"Email {new_email} is already in use by another account")
            return jsonify({
                'status': False,
                'message': 'Email already in use by another account',
                'error_type': 'email_exists'
            }), 400
              
        # Generate verification code
        code = generate_verification_code(6)
        expires_at = datetime.utcnow() + timedelta(minutes=10)
        
        logger.info(f"Generated verification code for email change. Expires at: {expires_at.isoformat()}")
        
        # Store verification code and new email in user document
        user_data['email_change_code'] = code
        user_data['email_change_expires_at'] = expires_at.isoformat()
        user_data['new_email'] = new_email
        user_data['updated_at'] = datetime.utcnow().isoformat()
        
        # Reset failed attempts if there were any
        user_data.pop('email_change_failed_attempts', None)
        user_data.pop('email_change_lockout_until', None)
        
        # Log the user data keys for debugging
        logger.info(f"User document keys after update: {list(user_data.keys())}")
        
        # Save updated user data
        try:
            client.save_document(db_name, user_data)
            logger.info(f"Email change requested for user {user_id} to new email {new_email}")
        except Exception as e:
            logger.error(f"Failed to save email change code: {str(e)}")
            return jsonify({
                'status': False,
                'message': 'Failed to process request',
                'error_type': 'server_error'
            }), 500
            
        # Send verification code to the new email
        email_subject = "Your Moodist Email Change Verification Code"
        email_body = f"""
You have requested to change your email address for your Moodist account.

Your verification code is: {code}

This code will expire in 10 minutes.
If you did not request this change, please ignore this email or contact support.

University of Melbourne - Moodist Platform
"""
        logger.info(f"Sending verification code to new email: {new_email}")
        email_sent = send_email(new_email, email_subject, email_body)
        if not email_sent:
            logger.error(f"Failed to send verification email to {new_email}")
            return jsonify({
                'status': False,
                'message': 'Failed to send verification code',
                'error_type': 'email_failure'
            }), 500
            
        logger.info(f"Verification code sent successfully to {new_email}")
        return jsonify({
            'status': True,
            'message': 'Verification code sent to new email address'
        }), 200
        
    except Exception as e:
        logger.error(f"Error in request_email_change: {str(e)}")
        return jsonify({
            'status': False,
            'message': 'Server error',
            'error_type': 'server_error'
        }), 500

@auth_bp.route('/verify-email-change', methods=['POST'])
@login_required
def verify_email_change():
    """
    Verify the email change code and update the user's email.
    Requires authentication.
    
    Request body:
    {
        "code": "123456",
        "password": "current_password" // For security verification
    }
    
    Returns:
        JSON: Status of the email change
    """
    try:
        # Log the request for debugging
        logger.info(f"Email change verification request received for user ID: {current_user.id}")
        
        data = request.get_json()
        if not data:
            logger.error("No JSON data provided in request body")
            return jsonify({
                'status': False,
                'message': 'No JSON data provided',
                'error_type': 'missing_data'
            }), 400
            
        # Log the received data (excluding password)
        safe_data = {k: v for k, v in data.items() if k != 'password'}
        logger.info(f"Email change verification data: {safe_data}")
        
        code = data.get('code', '').strip()
        password = data.get('password', '')
        
        if not code or not password:
            missing_fields = []
            if not code: missing_fields.append('code')
            if not password: missing_fields.append('password')
            logger.error(f"Missing required fields: {', '.join(missing_fields)}")
            return jsonify({
                'status': False,
                'message': 'Verification code and password are required',
                'error_type': 'missing_fields',
                'missing': missing_fields
            }), 400
            
        # Get user data from the session
        client = CouchDBClient()
        db_name = current_user.get_db_name()
        user_id = current_user.id
        
        logger.info(f"Fetching user data from database: {db_name}, user ID: {user_id}")
        
        # Fetch the latest user data directly from the database
        try:
            user_data = client.get_document(db_name, user_id)
            if not user_data:
                logger.error(f"Could not find user document for ID {user_id} in database {db_name}")
                return jsonify({
                    'status': False,
                    'message': 'User data not found',
                    'error_type': 'user_not_found'
                }), 404
        except Exception as e:
            logger.error(f"Error fetching user data: {str(e)}")
            return jsonify({
                'status': False,
                'message': 'Error retrieving user data',
                'error_type': 'database_error'
            }), 500
            
        logger.info(f"User data retrieved successfully. Email: {user_data.get('email')}")
        
        # Check for too many attempts
        failed_attempts = user_data.get('email_change_failed_attempts', 0)
        if failed_attempts >= 5:  # Limit to 5 attempts
            # Check if we're in lockout period
            lockout_until = user_data.get('email_change_lockout_until')
            if lockout_until:
                try:
                    lockout_until_dt = datetime.fromisoformat(lockout_until)
                    if datetime.utcnow() < lockout_until_dt:
                        remaining_seconds = int((lockout_until_dt - datetime.utcnow()).total_seconds())
                        logger.warning(f"User {user_id} is locked out for {remaining_seconds} more seconds")
                        return jsonify({
                            'status': False,
                            'message': f'Too many failed attempts. Try again in {remaining_seconds} seconds.',
                            'error_type': 'too_many_attempts',
                            'lockout_seconds': remaining_seconds
                        }), 429
                except Exception as e:
                    logger.warning(f"Error parsing lockout time: {str(e)}")
                    # If there's an error parsing the lockout time, reset it
                    pass
        
        # Verify password using the same method as in authentication
        stored_hash = user_data.get('password')
        if not stored_hash:
            logger.error(f"No password hash found for user {user_id}")
            return jsonify({
                'status': False,
                'message': 'Password verification failed',
                'error_type': 'invalid_password'
            }), 401
            
        # Use the verify_password function from token_generator
        if not verify_password(stored_hash, password):
            # Log the error for debugging
            logger.warning(f"Password verification failed for user {user_id} during email change")
            
            # Increment failed attempts
            user_data['email_change_failed_attempts'] = failed_attempts + 1
            
            # If reached threshold, set lockout
            if user_data['email_change_failed_attempts'] >= 5:
                lockout_until = datetime.utcnow() + timedelta(minutes=15)  # 15 minute lockout
                user_data['email_change_lockout_until'] = lockout_until.isoformat()
                
            # Save updated attempt count
            try:
                client.save_document(db_name, user_data)
            except Exception as e:
                logger.warning(f"Failed to update failed attempts: {str(e)}")
                
            return jsonify({
                'status': False,
                'message': 'Incorrect password',
                'error_type': 'invalid_password',
                'attempts_remaining': max(0, 5 - user_data['email_change_failed_attempts'])
            }), 401
            
        # Check verification code
        stored_code = user_data.get('email_change_code')
        expires_at = user_data.get('email_change_expires_at')
        new_email = user_data.get('new_email')
        
        # Log verification code check
        logger.info(f"Checking verification code. Stored code exists: {stored_code is not None}, " +
                   f"Expiration exists: {expires_at is not None}, " +
                   f"New email exists: {new_email is not None}")
        
        if not stored_code or not expires_at or not new_email:
            missing = []
            if not stored_code: missing.append('email_change_code')
            if not expires_at: missing.append('email_change_expires_at')
            if not new_email: missing.append('new_email')
            logger.error(f"Missing email change data: {', '.join(missing)}. Did you request an email change first?")
            return jsonify({
                'status': False,
                'message': 'No email change request found. Please request an email change first.',
                'error_type': 'no_request',
                'missing_fields': missing
            }), 400
            
        try:
            expires_at_dt = datetime.fromisoformat(expires_at)
        except Exception as e:
            logger.error(f"Invalid expiration format: {expires_at}, Error: {str(e)}")
            return jsonify({
                'status': False,
                'message': 'Invalid expiration format',
                'error_type': 'server_error'
            }), 400
            
        if code != stored_code:
            # Log the error for debugging
            logger.warning(f"Invalid verification code for user {user_id} during email change. Expected: {stored_code}, Got: {code}")
            
            # Increment failed attempts
            user_data['email_change_failed_attempts'] = failed_attempts + 1
            
            # If reached threshold, set lockout
            if user_data['email_change_failed_attempts'] >= 5:
                lockout_until = datetime.utcnow() + timedelta(minutes=15)  # 15 minute lockout
                user_data['email_change_lockout_until'] = lockout_until.isoformat()
                
            # Save updated attempt count
            try:
                client.save_document(db_name, user_data)
            except Exception as e:
                logger.warning(f"Failed to update failed attempts: {str(e)}")
                
            return jsonify({
                'status': False,
                'message': 'Invalid verification code',
                'error_type': 'invalid_code',
                'attempts_remaining': max(0, 5 - user_data['email_change_failed_attempts'])
            }), 400
            
        if datetime.utcnow() > expires_at_dt:
            logger.warning(f"Verification code expired. Expired at: {expires_at}, Current time: {datetime.utcnow().isoformat()}")
            return jsonify({
                'status': False,
                'message': 'Verification code has expired',
                'error_type': 'expired_code'
            }), 400
            
        # Update email
        old_email = user_data.get('email')
        user_data['email'] = new_email
        user_data['email_changed_at'] = datetime.utcnow().isoformat()
        user_data['previous_email'] = old_email
        user_data['updated_at'] = datetime.utcnow().isoformat()
        
        logger.info(f"Updating email from {old_email} to {new_email} for user {user_id}")
        
        # Remove email change fields
        user_data.pop('email_change_code', None)
        user_data.pop('email_change_expires_at', None)
        user_data.pop('new_email', None)
        user_data.pop('email_change_failed_attempts', None)
        user_data.pop('email_change_lockout_until', None)
        
        # Save updated user data
        try:
            client.save_document(db_name, user_data)
            logger.info(f"Successfully changed email for user {user_id} from {old_email} to {new_email}")
        except Exception as e:
            logger.error(f"Failed to update email: {str(e)}")
            return jsonify({
                'status': False,
                'message': 'Failed to update email',
                'error_type': 'server_error'
            }), 500
            
        # Send confirmation emails
        # 1. To new email
        new_email_subject = "Your Moodist Email Has Been Changed"
        new_email_body = f"""
Your email address for your Moodist account has been successfully changed to this email address.

If you did not make this change, please contact support immediately.

University of Melbourne - Moodist Platform
"""
        send_email(new_email, new_email_subject, new_email_body)
        
        # 2. To old email
        old_email_subject = "Your Moodist Email Has Been Changed"
        old_email_body = f"""
Your email address for your Moodist account has been changed to {new_email}.

If you did not make this change, please contact support immediately.

University of Melbourne - Moodist Platform
"""
        send_email(old_email, old_email_subject, old_email_body)
        
        # Update the session with the new email
        # The user model is already updated in the database
        # Force a reload of the user in the session
        login_user(User(user_data))
        
        logger.info(f"Email change complete. Session updated for user {user_id}")
        
        return jsonify({
            'status': True,
            'message': 'Email successfully changed',
            'email': new_email
        }), 200
        
    except Exception as e:
        logger.error(f"Error in verify_email_change: {str(e)}")
        return jsonify({
            'status': False,
            'message': 'Server error',
            'error_type': 'server_error'
        }), 500

@auth_bp.route('/change-user-id', methods=['POST'])
@login_required
def change_user_id():
    """
    Securely generate and assign a new 6-character user_id (unique_id) for the authenticated user.
    This will sever all connections with other users for privacy.
    
    Returns status true and the new user_id if successful, else false and a reason.
    """
    try:
        client = CouchDBClient()
        db_name = current_user.get_db_name()
        user_id = current_user.id
        
        # Fetch the latest user data directly from the database
        user_data = client.get_document(db_name, user_id)
        if not user_data:
            logger.error(f"Could not find user document for ID {user_id} in database {db_name}")
            return jsonify({
                'status': False,
                'message': 'User data not found',
                'error_type': 'user_not_found'
            }), 404
            
        # Get the current unique_id
        old_unique_id = user_data.get('unique_id')
        if not old_unique_id:
            logger.warning(f"User {user_id} does not have a unique_id")
            old_unique_id = user_id  # Fall back to document ID
        
        # Generate a new unique 6-character user_id
        # The improved generate_unique_id function already checks for conflicts
        # with both _id and unique_id fields across all databases
        new_user_id = generate_unique_id(current_user.user_type, client)
        if not new_user_id:
            logger.error("Failed to generate a unique user ID")
            return jsonify({
                'status': False,
                'message': 'Failed to generate a unique user ID',
                'error_type': 'generation_failed'
            }), 500
            
        # Ensure it's not the same as the current one
        if new_user_id == old_unique_id:
            logger.warning(f"Generated ID {new_user_id} is the same as current ID {old_unique_id}, trying again")
            new_user_id = generate_unique_id(current_user.user_type, client)
            if not new_user_id or new_user_id == old_unique_id:
                logger.error("Could not generate a different unique user ID")
                return jsonify({
                    'status': False,
                    'message': 'Could not generate a new unique user ID',
                    'error_type': 'generation_failed'
                }), 500
        
        # Update the user document
        user_data['unique_id'] = new_user_id
        user_data['previous_unique_id'] = old_unique_id
        user_data['unique_id_changed_at'] = datetime.utcnow().isoformat()
        user_data['updated_at'] = datetime.utcnow().isoformat()
        
        # Save the updated user document
        try:
            client.save_document(db_name, user_data)
            logger.info(f"User {user_id} changed unique_id from {old_unique_id} to {new_user_id}")
        except Exception as e:
            logger.error(f"Failed to update user_id: {str(e)}")
            return jsonify({
                'status': False,
                'message': 'Failed to update user_id',
                'error_type': 'update_failed'
            }), 500
        
        # Sever all connections associated with the old unique_id
        # Note: This is a placeholder for the actual implementation
        # In the future, this will interact with the connections database
        try:
            # Placeholder for future implementation:
            # 1. Find all connections where patient_id = old_unique_id OR clinician_id = old_unique_id
            # 2. For each connection:
            #    a. Update status to "revoked"
            #    b. Add reason: "user_id_change"
            #    c. Update updated_at timestamp
            # 3. Log the number of connections severed
            
            # For now, just log that this would happen
            logger.info(f"Would sever all connections for user with old ID: {old_unique_id}")
            
            # Example future code:
            # connections_db = client.get_db('connections')
            # query = {
            #     "$or": [
            #         {"patient_id": old_unique_id},
            #         {"clinician_id": old_unique_id}
            #     ]
            # }
            # connections = connections_db.find(query)
            # severed_count = 0
            # for conn in connections:
            #     conn['status'] = 'revoked'
            #     conn['reason'] = 'user_id_change'
            #     conn['updated_at'] = datetime.utcnow().isoformat()
            #     connections_db.save(conn)
            #     severed_count += 1
            # logger.info(f"Severed {severed_count} connections for user {user_id}")
            
        except Exception as e:
            # Log the error but continue - user ID change is still successful
            logger.error(f"Error severing connections: {str(e)}")
        
        # Update session
        login_user(User(user_data))
        
        return jsonify({
            'status': True,
            'new_user_id': new_user_id,
            'message': 'User ID changed successfully. Any existing connections have been severed.'
        }), 200
    except Exception as e:
        logger.error(f"Error in change_user_id: {str(e)}")
        return jsonify({
            'status': False,
            'message': 'Server error',
            'error_type': 'server_error'
        }), 500 