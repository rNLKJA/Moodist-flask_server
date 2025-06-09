#!/usr/bin/env python
"""Script to update the .env file with the correct configuration."""

import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_env_file():
    """Update the .env file with the correct configuration."""
    env_content = """# Flask configuration
FLASK_APP=wsgi.py
FLASK_CONFIG=development
FLASK_DEBUG=1
PORT=20001
HOST=0.0.0.0

# Security
SECRET_KEY=Univeristy-of-Melbourne-Psychiatry-Department-Moodist-Application
SECURITY_PASSWORD_SALT=Psychiatry
SECURITY_PASSWORD_PEPPER=rNLKJA

# Development settings  
LOG_LEVEL=DEBUG
SSL_ENABLED=true

# CORS settings (permissive for development)
CORS_ALLOW_ORIGINS=*

# SSL/TLS - Using your global certificates
SSL_CERT=certs/global-cert.pem
SSL_KEY=certs/global-key.pem

# CouchDB Configuration
COUCHDB_HOST=54.206.113.97
COUCHDB_PORT=20002
COUCHDB_USER=moodist
COUCHDB_PASSWORD=UniversityofMelbourneMoodistTeam2024
COUCHDB_DB=moodist

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=itdevelopertina@gmail.com
EMAIL_HOST_PASSWORD="xhscirbuygrjndke"
EMAIL_PORT=465
EMAIL_USE_SSL=True
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        logger.info("Successfully updated .env file")
        return True
    except Exception as e:
        logger.error(f"Failed to update .env file: {str(e)}")
        return False

if __name__ == "__main__":
    update_env_file() 