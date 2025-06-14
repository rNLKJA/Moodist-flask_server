#!/usr/bin/env python3
"""
Test CouchDB Connection Script using our CouchDB client
"""

import json
from src.utils.couchdb_client import get_couchdb
from datetime import datetime

def test_connection():
    """Test the CouchDB connection using our client"""
    print("Testing CouchDB connection using our client...")
    
    # Get the CouchDB client
    couch = get_couchdb()
    
    # Print connection details
    print(f"Host: {couch.host}")
    print(f"Port: {couch.port}")
    print(f"URL: {couch.couch_url}")
    print(f"Database: {couch.db_name}")
    print()
    
    # Get connection status
    status = couch.get_connection_status()
    if status['connected']:
        print("✓ Successfully connected to CouchDB!")
        print(f"  Server Info: {json.dumps(status.get('server_info', {}), indent=2)}")
        
        # Test database operations
        db = couch.get_db()
        if db:
            print("\n✓ Successfully connected to database")
            
            # Create a test document
            test_doc = {
                "type": "test",
                "name": "connection_test",
                "timestamp": datetime.utcnow().isoformat(),
                "status": "success"
            }
            
            print("\nInserting test document...")
            result = couch.create_document(test_doc)
            
            if result:
                doc_id = result.get('id')
                print(f"✓ Document created with ID: {doc_id}")
                
                # Retrieve the document
                print("\nRetrieving document...")
                doc = couch.get_document("moodist", doc_id)
                if doc:
                    print(f"✓ Document retrieved: {json.dumps(dict(doc), indent=2)}")
                else:
                    print("✗ Failed to retrieve document")
            else:
                print("✗ Failed to create document")
        else:
            print("✗ Failed to get database")
    else:
        print(f"❌ Failed to connect to CouchDB: {status.get('error', 'Unknown error')}")
    
    print("\nConnection test complete.")

if __name__ == "__main__":
    test_connection() 