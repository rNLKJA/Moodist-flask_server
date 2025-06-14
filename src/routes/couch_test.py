"""CouchDB test routes."""

from flask import Blueprint, jsonify, request
from src.utils.couchdb_client import get_couchdb
from datetime import datetime

couch_test = Blueprint('couch_test', __name__, url_prefix='/api/couch')

@couch_test.route('/status', methods=['GET'])
def connection_status():
    """Check CouchDB connection status."""
    couch = get_couchdb()
    connected = couch.connect()
    
    if connected:
        return jsonify({
            'status': 'connected',
            'url': couch.couch_url,
            'database': couch.db_name
        })
    else:
        return jsonify({
            'status': 'disconnected',
            'url': couch.couch_url,
            'error': 'Could not connect to CouchDB'
        }), 500

@couch_test.route('/hello', methods=['GET'])
def hello_world():
    """Get hello world message from CouchDB."""
    couch = get_couchdb()
    
    # Try to find the hello world document by ID
    hello_doc = couch.get_document('moodist', 'hello_world')
    
    # If it doesn't exist, create it
    if not hello_doc:
        result = couch.create_document({
            '_id': 'hello_world',
            'type': 'greeting',
            'message': 'Hello, World from CouchDB!',
            'created_at': datetime.utcnow().isoformat()
        })
        if result:
            hello_doc = couch.get_document('moodist', 'hello_world')
        else:
            return jsonify({
                'error': 'Failed to create hello world document',
                'status': 'error'
            }), 500
    
    # Return the document
    return jsonify({
        'message': hello_doc.get('message', 'Hello, World!'),
        'created_at': hello_doc.get('created_at', datetime.utcnow().isoformat()),
        'status': 'success'
    })

@couch_test.route('/message', methods=['POST'])
def create_message():
    """Create a new message in CouchDB."""
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({
            'error': 'Message is required',
            'status': 'error'
        }), 400
    
    couch = get_couchdb()
    result = couch.create_document({
        'type': 'message',
        'message': data['message'],
        'created_at': datetime.utcnow().isoformat()
    })
    
    if result:
        return jsonify({
            'message': 'Message created successfully',
            'id': result.get('id'),
            'status': 'success'
        }), 201
    else:
        return jsonify({
            'error': 'Failed to create message',
            'status': 'error'
        }), 500

@couch_test.route('/messages', methods=['GET'])
def get_messages():
    """Get all messages from CouchDB."""
    couch = get_couchdb()
    db = couch.get_db()
    
    if not db:
        return jsonify({
            'error': 'Database connection failed',
            'status': 'error'
        }), 500
    
    # Query for messages using a temporary view (not efficient for production)
    messages = []
    for doc_id in db:
        doc = db[doc_id]
        if doc.get('type') == 'message':
            # Add the document ID to the message
            doc_copy = dict(doc)
            doc_copy['_id'] = doc_id
            messages.append(doc_copy)
    
    return jsonify({
        'messages': messages,
        'count': len(messages),
        'status': 'success'
    }) 