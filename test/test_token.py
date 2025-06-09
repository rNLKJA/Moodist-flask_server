#!/usr/bin/env python
"""Test script to verify token generation and CouchDB connection."""

import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Print environment variables for debugging
logger.info("Environment variables:")
logger.info(f"SECRET_KEY: {'set' if os.environ.get('SECRET_KEY') else 'not set'}")
logger.info(f"SECURITY_PASSWORD_SALT: {'set' if os.environ.get('SECURITY_PASSWORD_SALT') else 'not set'}")
logger.info(f"SECURITY_PASSWORD_PEPPER: {'set' if os.environ.get('SECURITY_PASSWORD_PEPPER') else 'not set'}")
logger.info(f"COUCHDB_HOST: {os.environ.get('COUCHDB_HOST', 'not set')}")
logger.info(f"COUCHDB_PORT: {os.environ.get('COUCHDB_PORT', 'not set')}")

# Test token generation
from src.utils.token_generator import generate_token, generate_verification_code

def test_token_generation():
    """Test token generation."""
    logger.info("Testing token generation...")
    verification_code = generate_verification_code()
    logger.info(f"Generated verification code: {verification_code}")
    
    token = generate_token("test@example.com", verification_code)
    logger.info(f"Generated token: {'success' if token else 'failed'}")
    
    return token is not None

# Test CouchDB connection
from src.utils.couchdb_client import get_couchdb

def test_couchdb_connection():
    """Test CouchDB connection."""
    logger.info("Testing CouchDB connection...")
    couch = get_couchdb()
    status = couch.get_connection_status()
    
    logger.info(f"Connection status: {status['connected']}")
    if not status['connected']:
        logger.error(f"Connection error: {status.get('error')}")
        logger.info(f"Connection URL: {status['url']}")
    else:
        logger.info("CouchDB connection successful!")
        
    return status['connected']

if __name__ == "__main__":
    token_result = test_token_generation()
    couchdb_result = test_couchdb_connection()
    
    if token_result and couchdb_result:
        logger.info("All tests passed!")
    else:
        logger.error("Tests failed!")
        if not token_result:
            logger.error("Token generation failed!")
        if not couchdb_result:
            logger.error("CouchDB connection failed!") 