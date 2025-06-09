"""Authentication routes for user registration and verification."""

import logging
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, url_for
from src.utils.couchdb_client import CouchDBClient
from src.utils.token_generator import (
    generate_verification_link_token, verify_link_token, hash_password
)
from src.utils.email_sender import send_email

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
    """Generate a unique 6-character uppercase ID for the user."""
    import string
    import secrets
    
    max_attempts = 50
    for attempt in range(max_attempts):
        # Generate 6-character uppercase ID
        unique_id = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        
        # Check if ID exists in any database
        databases_to_check = ['patient', 'clinician', 'moodist']
        id_exists = False
        
        for db in databases_to_check:
            try:
                # Check if document with this ID exists
                try:
                    doc = client.get_document(db, unique_id)
                    if doc:
                        id_exists = True
                        break
                except:
                    pass
                
                # Also check if any document has this as unique_id field
                result = client.find_documents(db, {"unique_id": unique_id}, limit=1)
                if result:
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

        # Generate a unique 6-character ID for the document
        document_id = None
        if existing_user:
            # Use existing ID if updating
            document_id = existing_user.get('_id')
        else:
            # Generate new 6-character ID for new users
            document_id = generate_unique_id(user_type, client)
            if not document_id:
                return jsonify({
                    'status': 'error',
                    'message': 'Failed to generate unique document ID'
                }), 500

        # Create user object with 6-character ID
        user_data = {
            "_id": document_id,  # Use 6-character ID as document _id
            'type': user_type,
            'user_type': user_type,
            'email': email,
            'password': password_hash,
            'is_verified': False,
            'status': 'pending_verification',
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
            'verification_token': verification_token,
            'token_expires_at': expires_at.isoformat()
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
        verification_url = f"https://localhost:20001/auth/verify-link/{verification_token}"
        
        # Send verification email
        email_subject = "Verify Your Moodist Account - Action Required (7 Days)"
        email_template = f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background-color: #f8f9fa; padding: 30px; border-radius: 10px;">
                    <h2 style="color: #2c3e50; text-align: center; margin-bottom: 30px;">
                        Welcome to Moodist! 
                    </h2>
                    
                    <p style="font-size: 16px; line-height: 1.6; color: #333333;">
                        Hello,
                    </p>
                    
                    <p style="font-size: 16px; line-height: 1.6; color: #34495e;">
                        Thank you for signing up for Moodist as an user. 
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
            return "Email verified"

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
        user['unique_id'] = unique_id  # Secondary unique identifier
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
            
            # Return simple text response
            return "Email verified"

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