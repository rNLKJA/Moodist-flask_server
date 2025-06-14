"""CouchDB utility functions with multi-database support."""

import os
import requests
import json
import logging
from datetime import datetime
import couchdb

# Configure logger
logger = logging.getLogger(__name__)

class CouchDBClient:
    """CouchDB connection and utility class with multi-database support."""
    
    _instance = None
    _server = None
    _databases = {}
    
    @classmethod
    def get_instance(cls):
        """Singleton pattern to ensure only one CouchDB instance."""
        if cls._instance is None:
            cls._instance = CouchDBClient()
        return cls._instance
    
    def __init__(self):
        """Initialize CouchDB connection."""
        # Get connection parameters from environment variables with defaults
        self.host = os.environ.get('COUCHDB_HOST', 'localhost')
        self.port = int(os.environ.get('COUCHDB_PORT', 20002))
        self.username = os.environ.get('COUCHDB_USER', 'moodist')
        self.password = os.environ.get('COUCHDB_PASSWORD', 'UniversityofMelbourneMoodistTeam2024')
        
        # Build the URL from components
        self.couch_url = f"http://{self.host}:{self.port}"
        self.auth = (self.username, self.password)
        
        self._server = None
        self._databases = {}
    
    def connect(self):
        """Connect to CouchDB."""
        if self._server is None:
            try:
                # Use the couchdb library with our URL and auth
                self._server = couchdb.Server(self.couch_url)
                self._server.resource.credentials = self.auth
                
                # Test the connection
                self._server.version()
                
                logger.info(f"Connected to CouchDB at {self.couch_url}")
                return True
            except Exception as e:
                logger.error(f"Failed to connect to CouchDB: {e}")
                return False
        return True
    
    def get_db(self, db_name="moodist"):
        """
        Get database instance for the specified database.
        
        Args:
            db_name (str): Database name (patient, doctor, admin, or moodist for general)
            
        Returns:
            Database instance or None
        """
        if not self.connect():
            logger.warning("Failed to connect to CouchDB")
            return None
        
        # Return cached database if available
        if db_name in self._databases:
            return self._databases[db_name]
        
        try:
            # Check if database exists, create if not
            if db_name not in self._server:
                self._databases[db_name] = self._server.create(db_name)
                logger.info(f"Created database '{db_name}'")
            else:
                self._databases[db_name] = self._server[db_name]
                logger.info(f"Connected to existing database '{db_name}'")
            
            return self._databases[db_name]
            
        except Exception as e:
            logger.error(f"Failed to get/create database '{db_name}': {e}")
            return None
    
    def get_user_database(self, user_type):
        """
        Get the appropriate database for a user type.
        
        Args:
            user_type (str): User type (patient, doctor, admin)
            
        Returns:
            Database instance
        """
        # Map user types to database names
        database_mapping = {
            'patient': 'patient',
            'doctor': 'clinician',  # Based on your screenshot
            'admin': 'moodist'      # Admins go to main moodist database
        }
        
        db_name = database_mapping.get(user_type, 'moodist')
        return self.get_db(db_name)
    
    def get_connection_status(self):
        """Get the connection status and details."""
        status = {
            'connected': False,
            'host': self.host,
            'port': self.port,
            'url': self.couch_url,
            'error': None
        }
        
        try:
            # Test connection directly using requests
            response = requests.get(f"{self.couch_url}/", auth=self.auth)
            response.raise_for_status()
            
            # If we get here, connection is successful
            status['connected'] = True
            status['server_info'] = response.json()
            
        except requests.exceptions.ConnectionError as e:
            status['error'] = f"Connection error: {str(e)}"
        except requests.exceptions.HTTPError as e:
            status['error'] = f"HTTP error: {str(e)}"
        except Exception as e:
            status['error'] = f"Unexpected error: {str(e)}"
            
        return status
    
    def create_document(self, document, db_name="moodist"):
        """Create a document in the specified database."""
        db = self.get_db(db_name)
        if db:
            try:
                doc_id, doc_rev = db.save(document)
                return {'id': doc_id, 'rev': doc_rev}
            except Exception as e:
                logger.error(f"Failed to create document: {e}")
        return None
    
    def get_document(self, db_name, doc_id):
        """
        Get a document from the specified database.
        
        Args:
            db_name (str): Database name
            doc_id (str): Document ID
            
        Returns:
            dict or None: Document if found, None otherwise
        """
        db = self.get_db(db_name)
        if not db:
            return None
            
        try:
            if doc_id in db:
                return db[doc_id]
            return None
        except Exception as e:
            if "not_found" not in str(e):  # Only log actual errors
                logger.error(f"Error getting document {doc_id} from {db_name}: {str(e)}")
            return None
    
    def update_document(self, doc_id, updates, db_name="moodist"):
        """Update a document in the specified database."""
        db = self.get_db(db_name)
        if db and doc_id in db:
            doc = db[doc_id]
            for key, value in updates.items():
                doc[key] = value
            return db.save(doc)
        return None
    
    def delete_document(self, doc_id, db_name="moodist"):
        """Delete a document from the specified database."""
        db = self.get_db(db_name)
        if db and doc_id in db:
            doc = db[doc_id]
            return db.delete(doc)
        return None
    
    def query_view(self, design_doc, view_name, db_name="moodist", **kwargs):
        """Query a view from a design document in the specified database."""
        db = self.get_db(db_name)
        if db:
            try:
                return db.view(f"{design_doc}/{view_name}", **kwargs)
            except Exception as e:
                logger.error(f"Failed to query view {design_doc}/{view_name}: {e}")
        return None
    
    def close(self):
        """Close the CouchDB connection."""
        # CouchDB client doesn't require explicit connection closing
        self._server = None
        self._databases = {}
        logger.info("Closed CouchDB connection")
    
    def list_databases(self):
        """List all available databases."""
        if not self.connect():
            return []
        
        try:
            # Return list of database names
            return list(self._server)
        except Exception as e:
            logger.error(f"Failed to list databases: {e}")
            return []
    
    def save_document(self, db_name, document):
        """Save a document to the specified database."""
        db = self.get_db(db_name)
        if db:
            try:
                # If document has _id and _rev, it's an update; otherwise, it's a new document
                doc_id, doc_rev = db.save(document)
                logger.info(f"Saved document to {db_name}: {doc_id}")
                return {'id': doc_id, 'rev': doc_rev, 'ok': True}
            except Exception as e:
                logger.error(f"Failed to save document to {db_name}: {e}")
                raise e
        else:
            raise Exception(f"Could not access database {db_name}")
    
    def find_documents(self, db_name, selector, limit=None):
        """
        Find documents in the database using a selector.
        
        Args:
            db_name (str): Database name
            selector (dict): Query selector (e.g., {"email": "user@example.com"})
            limit (int): Maximum number of documents to return
            
        Returns:
            list: List of matching documents
        """
        db = self.get_db(db_name)
        if not db:
            return []
        
        try:
            # For simple key-value queries, we can iterate through documents
            # This is not the most efficient for large databases, but works for our use case
            results = []
            
            for doc_id in db:
                try:
                    doc = db[doc_id]
                    
                    # Check if document matches selector
                    matches = True
                    for key, value in selector.items():
                        if key not in doc or doc[key] != value:
                            matches = False
                            break
                    
                    if matches:
                        results.append(doc)
                        
                        # Apply limit if specified
                        if limit and len(results) >= limit:
                            break
                            
                except Exception as e:
                    logger.debug(f"Skipping document {doc_id}: {e}")
                    continue
            
            logger.info(f"Found {len(results)} documents in {db_name} matching {selector}")
            return results
            
        except Exception as e:
            logger.error(f"Error finding documents in {db_name}: {e}")

# Create a singleton instance
couch_db = CouchDBClient.get_instance()

def get_couchdb():
    """Get the CouchDB singleton instance."""
    return couch_db 