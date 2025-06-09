#!/usr/bin/env python
"""Test script to verify the complete user creation flow."""

import os
import json
import requests
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Set the necessary environment variables for the test
os.environ['SECRET_KEY'] = "Univeristy-of-Melbourne-Psychiatry-Department-Moodist-Application"
os.environ['SECURITY_PASSWORD_SALT'] = "Psychiatry"
os.environ['SECURITY_PASSWORD_PEPPER'] = "rNLKJA"
os.environ['COUCHDB_HOST'] = "54.206.113.97"
os.environ['COUCHDB_PORT'] = "20002"
os.environ['COUCHDB_USER'] = "moodist"
os.environ['COUCHDB_PASSWORD'] = "UniversityofMelbourneMoodistTeam2024"

def test_user_creation():
    """Test the user creation endpoint."""
    logger.info("Testing user creation endpoint...")
    
    # Define the test user data
    test_user = {
        "email": "test@example.com",
        "password": "TestPassword123!",
        "first_name": "Test",
        "last_name": "User"
    }
    
    # Define the API endpoint
    url = "https://localhost:20001/auth/create-user/patient"
    
    try:
        # Make the API request (ignoring SSL verification for localhost)
        response = requests.post(url, json=test_user, verify=False)
        
        # Print the response
        logger.info(f"Status code: {response.status_code}")
        logger.info(f"Response: {response.text}")
        
        # Check if the request was successful
        if response.status_code == 201:
            logger.info("User creation successful!")
            return True
        else:
            logger.error(f"User creation failed with status code: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"Error making API request: {str(e)}")
        return False

if __name__ == "__main__":
    # Run the test
    result = test_user_creation()
    
    if result:
        logger.info("Test passed!")
    else:
        logger.error("Test failed!") 