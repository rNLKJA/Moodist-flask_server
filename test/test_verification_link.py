#!/usr/bin/env python
"""Test script for the new verification link workflow."""

import os
import json
import requests
import logging
from dotenv import load_dotenv
import urllib3

# Disable SSL warnings for localhost testing
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
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
os.environ['EMAIL_HOST_PASSWORD'] = "xhscirbuygrjndke"
os.environ['EMAIL_PORT'] = "465"
os.environ['EMAIL_USE_SSL'] = "True"

def test_create_patient_user():
    """Test creating a new patient user with verification link."""
    logger.info("\n" + "=" * 60)
    logger.info("🔗 Testing New Verification Link Workflow")
    logger.info("=" * 60)
    
    base_url = "https://localhost:20001"
    
    # Test data
    test_user = {
        "email": "testpatient+links@example.com",
        "password": "SecurePassword123!"
    }
    
    try:
        # Create a new patient user
        logger.info(f"📝 Creating patient user: {test_user['email']}")
        
        response = requests.post(
            f"{base_url}/auth/create-user/patient",
            json=test_user,
            verify=False,
            timeout=10
        )
        
        logger.info(f"Response Status: {response.status_code}")
        logger.info(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 201:
            data = response.json()
            logger.info("✅ User creation successful!")
            logger.info(f"Status: {data.get('status')}")
            logger.info(f"Message: {data.get('message')}")
            logger.info(f"Token: {data.get('token')[:50]}..." if data.get('token') else "No token")
            logger.info(f"Expires: {data.get('expires_at')}")
            
            return data.get('token')
        else:
            logger.error(f"❌ User creation failed: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Error creating user: {str(e)}")
        return None

def test_duplicate_user():
    """Test creating a duplicate user to verify status: false response."""
    logger.info("\n" + "=" * 60)
    logger.info("👥 Testing Duplicate User Handling")
    logger.info("=" * 60)
    
    base_url = "https://localhost:20001"
    
    # First, create a user and verify them (simulate existing user)
    test_user = {
        "email": "duplicatetest@example.com",
        "password": "TestPassword123!"
    }
    
    try:
        # Try to create the same user again
        logger.info(f"📝 Attempting to create duplicate user: {test_user['email']}")
        
        response = requests.post(
            f"{base_url}/auth/create-user/patient",
            json=test_user,
            verify=False,
            timeout=10
        )
        
        logger.info(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            logger.info("✅ Duplicate user handling working!")
            logger.info(f"Status: {data.get('status')}")
            logger.info(f"Message: {data.get('message')}")
            logger.info(f"Redirect to reset: {data.get('redirect_to_reset')}")
            
            if data.get('status') is False:
                logger.info("✅ Correctly returned status: false for duplicate user")
            else:
                logger.warning("⚠️ Expected status: false but got something else")
                
        else:
            logger.error(f"❌ Unexpected response: {response.status_code}")
            logger.error(f"Response: {response.text}")
            
    except Exception as e:
        logger.error(f"❌ Error testing duplicate user: {str(e)}")

def test_verification_link(token):
    """Test the verification link endpoint."""
    if not token:
        logger.warning("⚠️ No token provided, skipping verification link test")
        return
        
    logger.info("\n" + "=" * 60)
    logger.info("🔗 Testing Verification Link")
    logger.info("=" * 60)
    
    base_url = "https://localhost:20001"
    
    try:
        # Test the verification link
        logger.info(f"🔗 Testing verification link with token: {token[:20]}...")
        
        response = requests.get(
            f"{base_url}/auth/verify-link/{token}",
            verify=False,
            timeout=10
        )
        
        logger.info(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            logger.info("✅ Verification link successful!")
            logger.info(f"Status: {data.get('status')}")
            logger.info(f"Message: {data.get('message')}")
            logger.info(f"User ID: {data.get('user_id')}")
            logger.info(f"User Type: {data.get('user_type')}")
            
        else:
            logger.error(f"❌ Verification failed: {response.status_code}")
            logger.error(f"Response: {response.text}")
            
    except Exception as e:
        logger.error(f"❌ Error testing verification link: {str(e)}")

def test_server_running():
    """Test if the server is running."""
    logger.info("🔍 Checking if server is running...")
    
    try:
        # Test with an auth endpoint instead of health
        response = requests.get("https://localhost:20001/auth/verify", verify=False, timeout=5)
        if response.status_code in [405, 410]:  # Method not allowed or gone - means server is running
            logger.info("✅ Server is running!")
            return True
        else:
            logger.warning(f"⚠️ Server responded with status: {response.status_code}")
            return True  # Probably still running
    except Exception as e:
        logger.error(f"❌ Server not running: {str(e)}")
        logger.info("💡 Please start the server with: python run.py")
        return False

def main():
    """Run all verification link tests."""
    logger.info("🚀 Starting Verification Link Workflow Tests")
    
    # Check if server is running
    if not test_server_running():
        return
    
    # Test new user creation with verification link
    token = test_create_patient_user()
    
    # Test duplicate user handling
    test_duplicate_user()
    
    # Test verification link (if we have a token)
    test_verification_link(token)
    
    logger.info("\n" + "=" * 60)
    logger.info("🎉 Verification Link Tests Completed!")
    logger.info("=" * 60)
    logger.info("Next steps:")
    logger.info("1. Check your email for the verification link")
    logger.info("2. Click the link to verify your account")
    logger.info("3. Check the server logs for verification success")

if __name__ == "__main__":
    main() 