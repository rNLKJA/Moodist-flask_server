"""Patient-Clinician connection routes with JWT authentication."""

import logging
from datetime import datetime
from functools import wraps
from flask import Blueprint, request, jsonify, current_app
from src.utils.couchdb_client import CouchDBClient
from src.utils.id_generator import validate_unique_id
import jwt
import uuid

# Configure logger
logger = logging.getLogger(__name__)

# Create blueprint
connection_bp = Blueprint('connection', __name__, url_prefix='/api/connections')

def require_jwt_auth(f):
    """
    Decorator to require JWT authentication for clinician endpoints.
    
    Validates the JWT token against the database and extracts clinician_id.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({
                'success': False,
                'error': 'MISSING_TOKEN',
                'message': 'Authorization header is required'
            }), 401
        
        # Extract token from "Bearer <token>"
        try:
            token = auth_header.split(' ')[1]
        except IndexError:
            return jsonify({
                'success': False,
                'error': 'INVALID_TOKEN_FORMAT',
                'message': 'Authorization header must be in format: Bearer <token>'
            }), 401
        
        try:
            # Decode JWT token
            secret_key = current_app.config.get('SECRET_KEY', 'your-secret-key')
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            
            # Validate token in database
            client = CouchDBClient()
            tokens = client.find_documents('auth_tokens', {
                'access_token': token,
                'active': True
            }, limit=1)
            
            if not tokens:
                return jsonify({
                    'success': False,
                    'error': 'INVALID_TOKEN',
                    'message': 'Token not found or inactive'
                }), 401
            
            # Check if token is expired
            token_doc = tokens[0]
            expires_at = datetime.fromisoformat(token_doc['expires_at'])
            if datetime.utcnow() > expires_at:
                return jsonify({
                    'success': False,
                    'error': 'TOKEN_EXPIRED',
                    'message': 'Token has expired'
                }), 401
            
            # Add clinician_id to request context
            request.clinician_id = payload['clinician_id']
            request.clinician_email = payload['email']
            
            return f(*args, **kwargs)
            
        except jwt.ExpiredSignatureError:
            return jsonify({
                'success': False,
                'error': 'TOKEN_EXPIRED',
                'message': 'Token has expired'
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                'success': False,
                'error': 'INVALID_TOKEN',
                'message': 'Invalid token'
            }), 401
        except Exception as e:
            logger.error(f"JWT authentication error: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'AUTHENTICATION_ERROR',
                'message': 'Authentication failed'
            }), 500
    
    return decorated_function

@connection_bp.route('/connect', methods=['POST'])
@require_jwt_auth
def connect_to_patient():
    """
    Connect a clinician to a patient using the patient's unique_id.
    
    Expected JSON payload:
    {
        "patient_unique_id": "ABC123"
    }
    
    Returns:
    {
        "success": true,
        "message": "Successfully connected to patient",
        "data": {
            "connection_id": "uuid",
            "patient_unique_id": "ABC123",
            "connected_at": "2025-01-01T12:00:00Z"
        }
    }
    """
    try:
        # Get request data
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'INVALID_REQUEST',
                'message': 'No JSON data provided'
            }), 400
        
        # Validate required fields
        patient_unique_id = data.get('patient_unique_id', '').strip().upper()
        
        if not patient_unique_id:
            return jsonify({
                'success': False,
                'error': 'MISSING_FIELD',
                'message': 'patient_unique_id is required'
            }), 400
        
        # Validate unique ID format
        if not validate_unique_id(patient_unique_id):
            return jsonify({
                'success': False,
                'error': 'INVALID_UNIQUE_ID',
                'message': 'Invalid patient unique ID format'
            }), 400
        
        # Initialize database client
        client = CouchDBClient()
        
        # Find patient by unique_id
        patients = client.find_documents('patient', {
            'unique_id': patient_unique_id
        }, limit=1)
        
        if not patients:
            return jsonify({
                'success': False,
                'error': 'PATIENT_NOT_FOUND',
                'message': 'Patient with this unique ID not found'
            }), 404
        
        patient = patients[0]
        patient_id = patient.get('_id')
        
        # Check if connection already exists
        existing_connections = client.find_documents('connections', {
            'clinician_id': request.clinician_id,
            'patient_id': patient_id,
            'patient_unique_id': patient_unique_id,
            'status': 'active'
        }, limit=1)
        
        if existing_connections:
            return jsonify({
                'success': False,
                'error': 'CONNECTION_EXISTS',
                'message': 'Connection already exists with this patient'
            }), 409
        
        # Create connection document
        connection_id = str(uuid.uuid4())
        connection_doc = {
            '_id': connection_id,
            'connection_id': connection_id,
            'clinician_id': request.clinician_id,
            'patient_id': patient_id,
            'patient_unique_id': patient_unique_id,
            'status': 'active',
            'reference_lines': [],  # Initialize empty reference lines array
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        # Save connection to database
        client.save_document('connections', connection_doc)
        
        logger.info(f"Connection created: {request.clinician_id} -> {patient_unique_id}")
        
        return jsonify({
            'success': True,
            'message': 'Successfully connected to patient',
            'data': {
                'connection_id': connection_id,
                'patient_unique_id': patient_unique_id,
                'connected_at': connection_doc['created_at']
            }
        }), 201
        
    except Exception as e:
        logger.error(f"Error in connect_to_patient: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'INTERNAL_ERROR',
            'message': 'An unexpected error occurred'
        }), 500

@connection_bp.route('/list', methods=['GET'])
@require_jwt_auth
def list_connections():
    """
    List all active connections for the authenticated clinician.
    
    Returns:
    {
        "success": true,
        "message": "Connections retrieved successfully",
        "data": {
            "connections": [
                {
                    "connection_id": "uuid",
                    "patient_unique_id": "ABC123",
                    "connected_at": "2025-01-01T12:00:00Z"
                }
            ],
            "total_count": 1
        }
    }
    """
    try:
        # Initialize database client
        client = CouchDBClient()
        
        # Find all active connections for this clinician
        connections = client.find_documents('connections', {
            'clinician_id': request.clinician_id,
            'status': 'active'
        })
        
        # Format response data
        formatted_connections = []
        for conn in connections:
            formatted_connections.append({
                'connection_id': conn.get('connection_id'),
                'patient_unique_id': conn.get('patient_unique_id'),
                'connected_at': conn.get('created_at')
            })
        
        # Sort by connection date (newest first)
        formatted_connections.sort(key=lambda x: x['connected_at'], reverse=True)
        
        return jsonify({
            'success': True,
            'message': 'Connections retrieved successfully',
            'data': {
                'connections': formatted_connections,
                'total_count': len(formatted_connections)
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error in list_connections: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'INTERNAL_ERROR',
            'message': 'An unexpected error occurred'
        }), 500

@connection_bp.route('/remove', methods=['DELETE'])
@require_jwt_auth
def remove_connection():
    """
    Remove a connection between clinician and patient.
    
    Expected JSON payload:
    {
        "connection_id": "uuid"
    }
    OR
    {
        "patient_unique_id": "ABC123"
    }
    
    Returns:
    {
        "success": true,
        "message": "Connection removed successfully"
    }
    """
    try:
        # Get request data
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'INVALID_REQUEST',
                'message': 'No JSON data provided'
            }), 400
        
        connection_id = data.get('connection_id', '').strip()
        patient_unique_id = data.get('patient_unique_id', '').strip().upper()
        
        if not connection_id and not patient_unique_id:
            return jsonify({
                'success': False,
                'error': 'MISSING_FIELD',
                'message': 'Either connection_id or patient_unique_id is required'
            }), 400
        
        # Initialize database client
        client = CouchDBClient()
        
        # Find connection to remove
        if connection_id:
            connections = client.find_documents('connections', {
                'connection_id': connection_id,
                'clinician_id': request.clinician_id,
                'status': 'active'
            }, limit=1)
        else:
            connections = client.find_documents('connections', {
                'patient_unique_id': patient_unique_id,
                'clinician_id': request.clinician_id,
                'status': 'active'
            }, limit=1)
        
        if not connections:
            return jsonify({
                'success': False,
                'error': 'CONNECTION_NOT_FOUND',
                'message': 'Connection not found'
            }), 404
        
        connection = connections[0]
        
        # Delete the connection document
        client.delete_document(connection['_id'], 'connections')
        
        logger.info(f"Connection removed: {request.clinician_id} -> {connection.get('patient_unique_id')}")
        
        return jsonify({
            'success': True,
            'message': 'Connection removed successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error in remove_connection: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'INTERNAL_ERROR',
            'message': 'An unexpected error occurred'
        }), 500

@connection_bp.route('/status/<patient_unique_id>', methods=['GET'])
@require_jwt_auth
def check_connection_status(patient_unique_id):
    """
    Check if a connection exists between clinician and patient.
    
    Returns:
    {
        "success": true,
        "message": "Connection status retrieved",
        "data": {
            "connected": true,
            "patient_unique_id": "ABC123",
            "connected_at": "2025-01-01T12:00:00Z"
        }
    }
    """
    try:
        # Validate unique ID format
        patient_unique_id = patient_unique_id.strip().upper()
        
        if not validate_unique_id(patient_unique_id):
            return jsonify({
                'success': False,
                'error': 'INVALID_UNIQUE_ID',
                'message': 'Invalid patient unique ID format'
            }), 400
        
        # Initialize database client
        client = CouchDBClient()
        
        # Find connection
        connections = client.find_documents('connections', {
            'clinician_id': request.clinician_id,
            'patient_unique_id': patient_unique_id,
            'status': 'active'
        }, limit=1)
        
        if connections:
            connection = connections[0]
            return jsonify({
                'success': True,
                'message': 'Connection status retrieved',
                'data': {
                    'connected': True,
                    'patient_unique_id': patient_unique_id,
                    'connected_at': connection.get('created_at')
                }
            }), 200
        else:
            return jsonify({
                'success': True,
                'message': 'Connection status retrieved',
                'data': {
                    'connected': False,
                    'patient_unique_id': patient_unique_id,
                    'connected_at': None
                }
            }), 200
        
    except Exception as e:
        logger.error(f"Error in check_connection_status: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'INTERNAL_ERROR',
            'message': 'An unexpected error occurred'
        }), 500


@connection_bp.route('/patient/<patient_unique_id>/mood-logs', methods=['GET'])
@require_jwt_auth
def get_patient_mood_logs(patient_unique_id):
    """
    Retrieve all mood logs for a specific patient based on their unique_patient_id.
    
    This endpoint allows clinicians to access mood log data for patients they are connected to.
    
    Args:
        patient_unique_id (str): The patient's unique ID
        
    Returns:
        JSON response containing all mood logs with timestamps, Q1-Q5 scores, and total scores
    """
    try:
        # Validate unique ID format
        if not validate_unique_id(patient_unique_id.strip().upper()):
            return jsonify({
                'success': False,
                'error': 'INVALID_UNIQUE_ID',
                'message': 'Invalid patient unique ID format'
            }), 400
        
        patient_unique_id = patient_unique_id.strip().upper()
        
        # Initialize database client
        client = CouchDBClient()
        
        # Check if clinician is connected to this patient
        connection_exists = client.find_documents('connections', {
            'clinician_id': request.clinician_id,
            'patient_unique_id': patient_unique_id,
            'status': 'active'
        }, limit=1)
        
        if not connection_exists:
            return jsonify({
                'success': False,
                'error': 'NO_CONNECTION',
                'message': 'You are not connected to this patient or connection does not exist'
            }), 403
        
        # Find patient by unique_id
        patients = client.find_documents('patient', {
            'unique_id': patient_unique_id
        }, limit=1)
        
        if not patients:
            return jsonify({
                'success': False,
                'error': 'PATIENT_NOT_FOUND',
                'message': 'Patient with this unique ID not found'
            }), 404
        
        patient = patients[0]
        patient_id = patient.get('_id')  # This is the actual patient _id like "MOKSAY"
        
        # Retrieve all mood logs for this patient
        # Search by user_id (which should match the patient's _id, not unique_id)
        mood_logs = client.find_documents('mood_logs', {
            'user_id': patient_id,
            'type': 'mood_log'
        })
        
        # Sort mood logs by timestamp (most recent first)
        mood_logs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        # Format the response data
        formatted_logs = []
        for log in mood_logs:
            formatted_log = {
                'log_id': log.get('_id'),
                'user_id': log.get('user_id'),
                'log_date': log.get('log_date'),
                'timestamp': log.get('timestamp'),
                'scores': {
                    'q1': log.get('scores', {}).get('q1'),
                    'q2': log.get('scores', {}).get('q2'),
                    'q3': log.get('scores', {}).get('q3'),
                    'q4': log.get('scores', {}).get('q4'),
                    'q5': log.get('scores', {}).get('q5')
                },
                'total_score': log.get('total_score'),
                'type': log.get('type')
            }
            formatted_logs.append(formatted_log)
        
        logger.info(f"Retrieved {len(formatted_logs)} mood logs for patient {patient_unique_id} by clinician {request.clinician_id}")
        
        return jsonify({
            'success': True,
            'message': f'Mood logs retrieved successfully for patient {patient_unique_id}',
            'data': {
                'patient_unique_id': patient_unique_id,
                'patient_id': patient.get('_id'),
                'total_logs': len(formatted_logs),
                'mood_logs': formatted_logs
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_patient_mood_logs: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'INTERNAL_ERROR',
            'message': 'An unexpected error occurred'
        }), 500 


@connection_bp.route('/patient/<patient_unique_id>/reference-lines', methods=['GET'])
@require_jwt_auth
def get_patient_reference_lines(patient_unique_id):
    """
    Get all reference lines for a specific patient-clinician connection.
    
    Reference lines are stored within the connection document and are automatically
    deleted when the connection is removed.
    
    Args:
        patient_unique_id (str): The patient's unique ID
        
    Returns:
        JSON response containing all reference lines for the connection
    """
    try:
        # Validate unique ID format
        if not validate_unique_id(patient_unique_id.strip().upper()):
            return jsonify({
                'success': False,
                'error': 'INVALID_UNIQUE_ID',
                'message': 'Invalid patient unique ID format'
            }), 400
        
        patient_unique_id = patient_unique_id.strip().upper()
        
        # Initialize database client
        client = CouchDBClient()
        
        # Find the connection between clinician and patient
        connections = client.find_documents('connections', {
            'clinician_id': request.clinician_id,
            'patient_unique_id': patient_unique_id,
            'status': 'active'
        }, limit=1)
        
        if not connections:
            return jsonify({
                'success': False,
                'error': 'NO_CONNECTION',
                'message': 'You are not connected to this patient or connection does not exist'
            }), 403
        
        connection = connections[0]
        
        # Get reference lines from the connection document
        reference_lines = connection.get('reference_lines', [])
        
        # Sort reference lines by datetime (most recent first)
        reference_lines.sort(key=lambda x: x.get('datetime', ''), reverse=True)
        
        logger.info(f"Retrieved {len(reference_lines)} reference lines for patient {patient_unique_id} by clinician {request.clinician_id}")
        
        return jsonify({
            'success': True,
            'message': f'Reference lines retrieved successfully for patient {patient_unique_id}',
            'data': {
                'patient_unique_id': patient_unique_id,
                'patient_id': connection.get('patient_id'),
                'connection_id': connection.get('connection_id'),
                'total_references': len(reference_lines),
                'reference_lines': reference_lines
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_patient_reference_lines: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'INTERNAL_ERROR',
            'message': 'An unexpected error occurred'
        }), 500


@connection_bp.route('/patient/<patient_unique_id>/reference-lines', methods=['POST'])
@require_jwt_auth
def add_patient_reference_line(patient_unique_id):
    """
    Add a new reference line to a patient-clinician connection.
    
    Expected JSON payload:
    {
        "description": "Started new medication",
        "datetime": "2025-07-10T12:00:00.000Z"  // Optional - defaults to current time
    }
    
    Args:
        patient_unique_id (str): The patient's unique ID
        
    Returns:
        JSON response with the created reference line
    """
    try:
        # Validate unique ID format
        if not validate_unique_id(patient_unique_id.strip().upper()):
            return jsonify({
                'success': False,
                'error': 'INVALID_UNIQUE_ID',
                'message': 'Invalid patient unique ID format'
            }), 400
        
        patient_unique_id = patient_unique_id.strip().upper()
        
        # Get request data
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'INVALID_REQUEST',
                'message': 'No JSON data provided'
            }), 400
        
        # Validate required fields
        description = data.get('description', '').strip()
        
        if not description:
            return jsonify({
                'success': False,
                'error': 'MISSING_FIELD',
                'message': 'description is required'
            }), 400
        
        if len(description) > 500:
            return jsonify({
                'success': False,
                'error': 'INVALID_FIELD',
                'message': 'description must be 500 characters or less'
            }), 400
        
        # Parse datetime (optional - defaults to current time)
        reference_datetime = data.get('datetime')
        if reference_datetime:
            try:
                from datetime import datetime as dt
                # Validate datetime format
                dt.fromisoformat(reference_datetime.replace('Z', '+00:00'))
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': 'INVALID_DATETIME',
                    'message': 'Invalid datetime format. Use ISO format (e.g., 2025-07-10T12:00:00.000Z)'
                }), 400
        else:
            reference_datetime = datetime.utcnow().isoformat() + 'Z'
        
        # Initialize database client
        client = CouchDBClient()
        
        # Find the connection between clinician and patient
        connections = client.find_documents('connections', {
            'clinician_id': request.clinician_id,
            'patient_unique_id': patient_unique_id,
            'status': 'active'
        }, limit=1)
        
        if not connections:
            return jsonify({
                'success': False,
                'error': 'NO_CONNECTION',
                'message': 'You are not connected to this patient or connection does not exist'
            }), 403
        
        connection = connections[0]
        
        # Get existing reference lines
        reference_lines = connection.get('reference_lines', [])
        
        # Generate new reference ID (auto-increment within the connection)
        ref_id = max([ref.get('ref_id', 0) for ref in reference_lines], default=0) + 1
        
        # Create new reference line
        new_reference = {
            'ref_id': ref_id,
            'datetime': reference_datetime,
            'description': description,
            'created_at': datetime.utcnow().isoformat() + 'Z',
            'clinician_id': request.clinician_id
        }
        
        # Add to reference lines array
        reference_lines.append(new_reference)
        
        # Update connection document
        connection['reference_lines'] = reference_lines
        connection['updated_at'] = datetime.utcnow().isoformat()
        
        # Save updated connection
        client.save_document('connections', connection)
        
        logger.info(f"Added reference line {ref_id} for patient {patient_unique_id} by clinician {request.clinician_id}")
        
        return jsonify({
            'success': True,
            'message': 'Reference line added successfully',
            'data': {
                'ref_id': ref_id,
                'datetime': reference_datetime,
                'description': description,
                'created_at': new_reference['created_at'],
                'patient_unique_id': patient_unique_id,
                'clinician_id': request.clinician_id
            }
        }), 201
        
    except Exception as e:
        logger.error(f"Error in add_patient_reference_line: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'INTERNAL_ERROR',
            'message': 'An unexpected error occurred'
        }), 500


@connection_bp.route('/patient/<patient_unique_id>/reference-lines/<int:ref_id>', methods=['PUT'])
@require_jwt_auth
def update_patient_reference_line(patient_unique_id, ref_id):
    """
    Update an existing reference line for a patient-clinician connection.
    
    Expected JSON payload:
    {
        "description": "Updated: Started new medication - dosage increased",
        "datetime": "2025-07-11T14:30:00.000Z"
    }
    
    Args:
        patient_unique_id (str): The patient's unique ID
        ref_id (int): The reference line ID to update
        
    Returns:
        JSON response with the updated reference line
    """
    try:
        # Validate unique ID format
        if not validate_unique_id(patient_unique_id.strip().upper()):
            return jsonify({
                'success': False,
                'error': 'INVALID_UNIQUE_ID',
                'message': 'Invalid patient unique ID format'
            }), 400
        
        patient_unique_id = patient_unique_id.strip().upper()
        
        # Get request data
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'INVALID_REQUEST',
                'message': 'No JSON data provided'
            }), 400
        
        # Validate required fields
        description = data.get('description', '').strip()
        
        if not description:
            return jsonify({
                'success': False,
                'error': 'MISSING_FIELD',
                'message': 'description is required'
            }), 400
        
        if len(description) > 500:
            return jsonify({
                'success': False,
                'error': 'INVALID_FIELD',
                'message': 'description must be 500 characters or less'
            }), 400
        
        # Parse datetime (optional)
        reference_datetime = data.get('datetime')
        if reference_datetime:
            try:
                from datetime import datetime as dt
                # Validate datetime format
                dt.fromisoformat(reference_datetime.replace('Z', '+00:00'))
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': 'INVALID_DATETIME',
                    'message': 'Invalid datetime format. Use ISO format (e.g., 2025-07-10T12:00:00.000Z)'
                }), 400
        
        # Initialize database client
        client = CouchDBClient()
        
        # Find the connection between clinician and patient
        connections = client.find_documents('connections', {
            'clinician_id': request.clinician_id,
            'patient_unique_id': patient_unique_id,
            'status': 'active'
        }, limit=1)
        
        if not connections:
            return jsonify({
                'success': False,
                'error': 'NO_CONNECTION',
                'message': 'You are not connected to this patient or connection does not exist'
            }), 403
        
        connection = connections[0]
        
        # Get existing reference lines
        reference_lines = connection.get('reference_lines', [])
        
        # Find the reference line to update
        reference_to_update = None
        for ref in reference_lines:
            if ref.get('ref_id') == ref_id:
                reference_to_update = ref
                break
        
        if not reference_to_update:
            return jsonify({
                'success': False,
                'error': 'REFERENCE_NOT_FOUND',
                'message': 'Reference line not found'
            }), 404
        
        # Update the reference line
        reference_to_update['description'] = description
        if reference_datetime:
            reference_to_update['datetime'] = reference_datetime
        reference_to_update['updated_at'] = datetime.utcnow().isoformat() + 'Z'
        
        # Update connection document
        connection['reference_lines'] = reference_lines
        connection['updated_at'] = datetime.utcnow().isoformat()
        
        # Save updated connection
        client.save_document('connections', connection)
        
        logger.info(f"Updated reference line {ref_id} for patient {patient_unique_id} by clinician {request.clinician_id}")
        
        return jsonify({
            'success': True,
            'message': 'Reference line updated successfully',
            'data': {
                'ref_id': ref_id,
                'datetime': reference_to_update['datetime'],
                'description': reference_to_update['description'],
                'created_at': reference_to_update.get('created_at'),
                'updated_at': reference_to_update.get('updated_at'),
                'patient_unique_id': patient_unique_id,
                'clinician_id': request.clinician_id
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error in update_patient_reference_line: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'INTERNAL_ERROR',
            'message': 'An unexpected error occurred'
        }), 500


@connection_bp.route('/patient/<patient_unique_id>/reference-lines/<int:ref_id>', methods=['DELETE'])
@require_jwt_auth
def delete_patient_reference_line(patient_unique_id, ref_id):
    """
    Delete a reference line from a patient-clinician connection.
    
    Args:
        patient_unique_id (str): The patient's unique ID
        ref_id (int): The reference line ID to delete
        
    Returns:
        JSON response confirming deletion
    """
    try:
        # Validate unique ID format
        if not validate_unique_id(patient_unique_id.strip().upper()):
            return jsonify({
                'success': False,
                'error': 'INVALID_UNIQUE_ID',
                'message': 'Invalid patient unique ID format'
            }), 400
        
        patient_unique_id = patient_unique_id.strip().upper()
        
        # Initialize database client
        client = CouchDBClient()
        
        # Find the connection between clinician and patient
        connections = client.find_documents('connections', {
            'clinician_id': request.clinician_id,
            'patient_unique_id': patient_unique_id,
            'status': 'active'
        }, limit=1)
        
        if not connections:
            return jsonify({
                'success': False,
                'error': 'NO_CONNECTION',
                'message': 'You are not connected to this patient or connection does not exist'
            }), 403
        
        connection = connections[0]
        
        # Get existing reference lines
        reference_lines = connection.get('reference_lines', [])
        
        # Find and remove the reference line
        original_count = len(reference_lines)
        reference_lines = [ref for ref in reference_lines if ref.get('ref_id') != ref_id]
        
        if len(reference_lines) == original_count:
            return jsonify({
                'success': False,
                'error': 'REFERENCE_NOT_FOUND',
                'message': 'Reference line not found'
            }), 404
        
        # Update connection document
        connection['reference_lines'] = reference_lines
        connection['updated_at'] = datetime.utcnow().isoformat()
        
        # Save updated connection
        client.save_document('connections', connection)
        
        logger.info(f"Deleted reference line {ref_id} for patient {patient_unique_id} by clinician {request.clinician_id}")
        
        return jsonify({
            'success': True,
            'message': 'Reference line deleted successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error in delete_patient_reference_line: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'INTERNAL_ERROR',
            'message': 'An unexpected error occurred'
        }), 500 