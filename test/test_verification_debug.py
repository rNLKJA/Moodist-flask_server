#!/usr/bin/env python
"""Debug test script for verification process."""

import os
import requests
import logging
from dotenv import load_dotenv
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Set environment variables
os.environ['SECRET_KEY'] = "Univeristy-of-Melbourne-Psychiatry-Department-Moodist-Application"
os.environ['SECURITY_PASSWORD_SALT'] = "Psychiatry"
os.environ['SECURITY_PASSWORD_PEPPER'] = "rNLKJA"

def test_simple_workflow():
    """Test a simple workflow to debug the verification issue."""
    base_url = "https://localhost:20001"
    test_email = "debug_test@example.com"
    
    # Step 1: Create user
    logger.info("Step 1: Creating user...")
    create_url = f"{base_url}/auth/create-user/patient"
    create_data = {
        "email": test_email,
        "password": "TestPassword123!",
        "first_name": "Debug",
        "last_name": "User"
    }
    
    try:
        response = requests.post(create_url, json=create_data, verify=False)
        logger.info(f"Create response status: {response.status_code}")
        logger.info(f"Create response: {response.text}")
        
        if response.status_code != 201:
            logger.error("Failed to create user")
            return False
        
        create_result = response.json()
        verification_token = create_result['verification_token']
        
        # Extract verification code
        verification_code = extract_verification_code(verification_token)
        logger.info(f"Extracted verification code: {verification_code}")
        
        # Step 2: Verify user
        logger.info("Step 2: Verifying user...")
        verify_url = f"{base_url}/auth/verify"
        verify_data = {
            "verification_token": verification_token,
            "verification_code": verification_code
        }
        
        response = requests.post(verify_url, json=verify_data, verify=False)
        logger.info(f"Verify response status: {response.status_code}")
        logger.info(f"Verify response: {response.text}")
        
        if response.status_code == 200:
            logger.info("✅ Verification successful!")
            return True
        else:
            logger.error("❌ Verification failed!")
            return False
            
    except Exception as e:
        logger.error(f"Error during test: {str(e)}")
        return False

def extract_verification_code(verification_token):
    """Extract verification code from token."""
    try:
        from itsdangerous import URLSafeTimedSerializer
        
        secret_key = os.environ.get('SECRET_KEY')
        salt = os.environ.get('SECURITY_PASSWORD_SALT')
        
        serializer = URLSafeTimedSerializer(secret_key)
        payload = serializer.loads(verification_token, salt=salt)
        return payload.get('code')
    except Exception as e:
        logger.error(f"Failed to extract verification code: {str(e)}")
        return None

if __name__ == "__main__":
    success = test_simple_workflow()
    if success:
        logger.info("🎉 Test completed successfully!")
    else:
        logger.error("💥 Test failed!")
        exit(1) 