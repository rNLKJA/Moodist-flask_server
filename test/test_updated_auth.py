#!/usr/bin/env python
"""Test script to verify the updated authentication system."""

import os
import json
import requests
import logging
from dotenv import load_dotenv

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
os.environ['EMAIL_HOST'] = "smtp.gmail.com"
os.environ['EMAIL_HOST_USER'] = "itdevelopertina@gmail.com"
os.environ['EMAIL_HOST_PASSWORD'] = "xhsc irbu ygrj ndke"
os.environ['EMAIL_PORT'] = "465"
os.environ['EMAIL_USE_SSL'] = "True"

def test_user_creation():
    """Test the user creation endpoint with the updated verification code system."""
    logger.info("Testing user creation endpoint...")
    
    # Define the test user data
    test_user = {
        "email": "test_updated@example.com",
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
            response_data = response.json()
            verification_token = response_data.get('token')
            
            # Check if the verification code is included in the token
            from src.utils.token_generator import verify_token
            
            # Extract the verification code from the token
            # Note: In a real scenario, this would be sent to the user's email
            # We're using this for testing purposes only
            import time
            from itsdangerous import URLSafeTimedSerializer
            
            secret_key = os.environ.get('SECRET_KEY')
            salt = os.environ.get('SECURITY_PASSWORD_SALT')
            
            serializer = URLSafeTimedSerializer(secret_key)
            payload = serializer.loads(verification_token, salt=salt)
            verification_code = payload.get('code')
            
            logger.info(f"Extracted verification code: {verification_code}")
            
            # Verify the code is 6 digits
            if verification_code and len(verification_code) == 6 and verification_code.isdigit():
                logger.info("Verification code is a valid 6-digit number!")
            else:
                logger.error(f"Verification code is not a valid 6-digit number: {verification_code}")
                return False
            
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