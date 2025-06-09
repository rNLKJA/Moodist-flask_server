"""Connection test routes."""

from flask import Blueprint, jsonify
from src.utils.couchdb_client import get_couchdb
import os
import json

connection_test = Blueprint('connection_test', __name__, url_prefix='/api/connection')

@connection_test.route('/test', methods=['GET'])
def test_connection():
    """Test the CouchDB connection and report detailed status."""
    couch = get_couchdb()
    status = couch.get_connection_status()
    
    # Prepare response
    response = {
        'database_type': 'CouchDB',
        'connection_status': 'success' if status['connected'] else 'failed',
        'connection_details': {
            'host': status['host'],
            'port': status['port'],
            'url': status['url'],
            'database': status['database']
        }
    }
    
    # Add server info if available
    if status.get('server_info'):
        response['server_info'] = status['server_info']
    
    # Add error information if connection failed
    if not status['connected']:
        response['error'] = status['error']
        return jsonify(response), 500
    
    # If connected, try to ping the database
    try:
        db = couch.get_db()
        if db:
            # Try to create a test document
            test_doc = {
                'type': 'connection_test',
                'message': 'Connection test successful',
                'timestamp': couch._server.version()  # Use server version as timestamp
            }
            result = couch.create_document(test_doc)
            if result:
                response['test_document'] = {
                    'created': True,
                    'id': result.get('id')
                }
            else:
                response['test_document'] = {
                    'created': False,
                    'error': 'Failed to create test document'
                }
        else:
            response['error'] = 'Database object is None'
            return jsonify(response), 500
    except Exception as e:
        response['error'] = f"Database operation failed: {str(e)}"
        return jsonify(response), 500
    
    return jsonify(response)

@connection_test.route('/env', methods=['GET'])
def check_env_vars():
    """Check for environment variables used for CouchDB connection."""
    couch = get_couchdb()
    
    env_status = {
        'connection_parameters': {
            'COUCHDB_HOST': os.environ.get('COUCHDB_HOST', 'Default: localhost'),
            'COUCHDB_PORT': os.environ.get('COUCHDB_PORT', 'Default: 20002'),
            'COUCHDB_USER': os.environ.get('COUCHDB_USER', 'Default: moodist'),
            'COUCHDB_PASSWORD': 'Set' if os.environ.get('COUCHDB_PASSWORD') else 'Using default',
            'COUCHDB_DB': os.environ.get('COUCHDB_DB', 'Default: moodist')
        },
        'effective_settings': {
            'host': couch.host,
            'port': couch.port,
            'url': couch.couch_url,
            'database': couch.db_name
        }
    }
    
    return jsonify(env_status) 