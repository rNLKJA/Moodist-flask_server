"""Patient routes for unique_id management and connection removal."""

import logging
from datetime import datetime
from flask import Blueprint, request, jsonify
from src.utils.couchdb_client import CouchDBClient
from src.utils.id_generator import generate_unique_id, validate_unique_id
import secrets
import string

# Configure logger
logger = logging.getLogger(__name__)

# Create blueprint
patient_bp = Blueprint('patient', __name__, url_prefix='/api/patient')

def generate_random_unique_id(length=6):
    """Generate a random unique ID without database validation."""
    return ''.join(secrets.choice(string.ascii_uppercase) for _ in range(length))

def remove_patient_connections(client, patient_id, old_patient_unique_id):
    """
    Remove all connections associated with a patient.
    
    Args:
        client: CouchDBClient instance
        patient_id: Patient's database ID
        old_patient_unique_id: Patient's old unique ID
    """
    try:
        # Find all connections for this patient by patient_id (most reliable)
        connections = client.find_documents('connections', {
            'patient_id': patient_id,
            'status': 'active'
        })
        
        # Delete all connections
        for connection in connections:
            client.delete_document(connection['_id'], 'connections')
            logger.info(f"Deleted connection: {connection['connection_id']} for patient {old_patient_unique_id}")
        
        logger.info(f"Removed {len(connections)} connections for patient {old_patient_unique_id}")
        
    except Exception as e:
        logger.error(f"Error removing connections for patient {patient_id}: {str(e)}")

@patient_bp.route('/generate-new-id', methods=['POST'])
def generate_new_unique_id():
    """
    Generate a new random unique_id for the patient and remove all connections.
    
    Expected JSON payload:
    {
        "current_unique_id": "ABC123"
    }
    
    Returns:
    {
        "success": true,
        "message": "New unique ID generated successfully",
        "data": {
            "old_unique_id": "ABC123",
            "new_unique_id": "XYZ789",
            "connections_removed": 5
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
        current_unique_id = data.get('current_unique_id', '').strip().upper()
        
        if not current_unique_id:
            return jsonify({
                'success': False,
                'error': 'MISSING_FIELD',
                'message': 'current_unique_id is required'
            }), 400
        
        # Validate unique ID format
        if not validate_unique_id(current_unique_id):
            return jsonify({
                'success': False,
                'error': 'INVALID_UNIQUE_ID',
                'message': 'Invalid current unique ID format'
            }), 400
        
        # Initialize database client
        client = CouchDBClient()
        
        # Find patient by current unique_id
        patients = client.find_documents('patient', {
            'unique_id': current_unique_id
        }, limit=1)
        
        if not patients:
            return jsonify({
                'success': False,
                'error': 'PATIENT_NOT_FOUND',
                'message': 'Patient with this unique ID not found'
            }), 404
        
        patient = patients[0]
        patient_id = patient.get('_id')
        
        # Count existing connections before removal
        existing_connections = client.find_documents('connections', {
            'patient_id': patient_id,
            'patient_unique_id': current_unique_id,
            'status': 'active'
        })
        connections_count = len(existing_connections)
        
        # Generate new unique ID
        new_unique_id = generate_random_unique_id()
        
        # Update patient document with new unique_id
        patient['unique_id'] = new_unique_id
        patient['updated_at'] = datetime.utcnow().isoformat()
        patient['unique_id_changed_at'] = datetime.utcnow().isoformat()
        
        # Save updated patient
        client.save_document('patient', patient)
        
        # Remove all existing connections
        remove_patient_connections(client, patient_id, current_unique_id)
        
        logger.info(f"Patient {patient_id} changed unique_id from {current_unique_id} to {new_unique_id}")
        
        return jsonify({
            'success': True,
            'message': 'New unique ID generated successfully',
            'data': {
                'old_unique_id': current_unique_id,
                'new_unique_id': new_unique_id,
                'connections_removed': connections_count
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error in generate_new_unique_id: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'INTERNAL_ERROR',
            'message': 'An unexpected error occurred'
        }), 500

@patient_bp.route('/change-id', methods=['POST'])
def change_unique_id():
    """
    Change patient's unique_id to a specific value and remove all connections.
    
    Expected JSON payload:
    {
        "current_unique_id": "ABC123",
        "new_unique_id": "XYZ789"
    }
    
    Returns:
    {
        "success": true,
        "message": "Unique ID changed successfully",
        "data": {
            "old_unique_id": "ABC123",
            "new_unique_id": "XYZ789",
            "connections_removed": 5
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
        current_unique_id = data.get('current_unique_id', '').strip().upper()
        new_unique_id = data.get('new_unique_id', '').strip().upper()
        
        if not current_unique_id or not new_unique_id:
            return jsonify({
                'success': False,
                'error': 'MISSING_FIELD',
                'message': 'Both current_unique_id and new_unique_id are required'
            }), 400
        
        # Validate unique ID formats
        if not validate_unique_id(current_unique_id) or not validate_unique_id(new_unique_id):
            return jsonify({
                'success': False,
                'error': 'INVALID_UNIQUE_ID',
                'message': 'Invalid unique ID format'
            }), 400
        
        # Check if new unique_id is different from current
        if current_unique_id == new_unique_id:
            return jsonify({
                'success': False,
                'error': 'SAME_UNIQUE_ID',
                'message': 'New unique ID must be different from current unique ID'
            }), 400
        
        # Initialize database client
        client = CouchDBClient()
        
        # Find patient by current unique_id
        patients = client.find_documents('patient', {
            'unique_id': current_unique_id
        }, limit=1)
        
        if not patients:
            return jsonify({
                'success': False,
                'error': 'PATIENT_NOT_FOUND',
                'message': 'Patient with this unique ID not found'
            }), 404
        
        # Check if new unique_id is already taken
        existing_patients = client.find_documents('patient', {
            'unique_id': new_unique_id
        }, limit=1)
        
        if existing_patients:
            return jsonify({
                'success': False,
                'error': 'UNIQUE_ID_TAKEN',
                'message': 'New unique ID is already taken'
            }), 409
        
        patient = patients[0]
        patient_id = patient.get('_id')
        
        # Count existing connections before removal
        existing_connections = client.find_documents('connections', {
            'patient_id': patient_id,
            'patient_unique_id': current_unique_id,
            'status': 'active'
        })
        connections_count = len(existing_connections)
        
        # Update patient document with new unique_id
        patient['unique_id'] = new_unique_id
        patient['updated_at'] = datetime.utcnow().isoformat()
        patient['unique_id_changed_at'] = datetime.utcnow().isoformat()
        
        # Save updated patient
        client.save_document('patient', patient)
        
        # Remove all existing connections
        remove_patient_connections(client, patient_id, current_unique_id)
        
        logger.info(f"Patient {patient_id} changed unique_id from {current_unique_id} to {new_unique_id}")
        
        return jsonify({
            'success': True,
            'message': 'Unique ID changed successfully',
            'data': {
                'old_unique_id': current_unique_id,
                'new_unique_id': new_unique_id,
                'connections_removed': connections_count
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error in change_unique_id: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'INTERNAL_ERROR',
            'message': 'An unexpected error occurred'
        }), 500

@patient_bp.route('/info', methods=['GET'])
def get_patient_info():
    """
    Get patient information by unique_id.
    
    Expected query parameter: unique_id
    
    Returns:
    {
        "success": true,
        "message": "Patient information retrieved",
        "data": {
            "patient_id": "abc123",
            "unique_id": "ABC123",
            "created_at": "2025-01-01T12:00:00Z",
            "updated_at": "2025-01-01T12:00:00Z"
        }
    }
    """
    try:
        # Get unique_id from query parameters
        unique_id = request.args.get('unique_id', '').strip().upper()
        
        if not unique_id:
            return jsonify({
                'success': False,
                'error': 'MISSING_PARAMETER',
                'message': 'unique_id query parameter is required'
            }), 400
        
        # Validate unique ID format
        if not validate_unique_id(unique_id):
            return jsonify({
                'success': False,
                'error': 'INVALID_UNIQUE_ID',
                'message': 'Invalid unique ID format'
            }), 400
        
        # Initialize database client
        client = CouchDBClient()
        
        # Find patient by unique_id
        patients = client.find_documents('patient', {
            'unique_id': unique_id
        }, limit=1)
        
        if not patients:
            return jsonify({
                'success': False,
                'error': 'PATIENT_NOT_FOUND',
                'message': 'Patient with this unique ID not found'
            }), 404
        
        patient = patients[0]
        
        # Return patient information (excluding sensitive data)
        return jsonify({
            'success': True,
            'message': 'Patient information retrieved',
            'data': {
                'patient_id': patient.get('_id'),
                'unique_id': patient.get('unique_id'),
                'created_at': patient.get('created_at'),
                'updated_at': patient.get('updated_at'),
                'unique_id_changed_at': patient.get('unique_id_changed_at')
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_patient_info: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'INTERNAL_ERROR',
            'message': 'An unexpected error occurred'
        }), 500 