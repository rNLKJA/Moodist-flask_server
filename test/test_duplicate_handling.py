#!/usr/bin/env python
"""Test script to verify duplicate user handling."""

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

def test_duplicate_user_workflow():
    """Test the complete duplicate user workflow."""
    logger.info("🔄 Testing Duplicate User Workflow")
    
    base_url = "https://localhost:20001"
    
    # Use a consistent test email
    test_user = {
        "email": "testduplicate@example.com",
        "password": "TestPassword123!"
    }
    
    logger.info(f"📝 Testing with email: {test_user['email']}")
    
    # Step 1: Create user for the first time
    logger.info("\n1️⃣ Creating user for the first time...")
    
    try:
        response1 = requests.post(
            f"{base_url}/auth/create-user/patient",
            json=test_user,
            verify=False,
            timeout=30
        )
        
        logger.info(f"First creation - Status: {response1.status_code}")
        logger.info(f"First creation - Response: {response1.text}")
        
        if response1.status_code == 201:
            data1 = response1.json()
            token = data1.get('token')
            logger.info("✅ First user creation successful")
            
            # Step 2: Verify the user to make them active
            logger.info("\n2️⃣ Verifying the user to make them active...")
            
            verify_response = requests.get(
                f"{base_url}/auth/verify-link/{token}",
                verify=False,
                timeout=30
            )
            
            logger.info(f"Verification - Status: {verify_response.status_code}")
            logger.info(f"Verification - Response: {verify_response.text}")
            
            if verify_response.status_code == 200:
                verify_data = verify_response.json()
                logger.info(f"✅ User verified successfully with ID: {verify_data.get('user_id')}")
                
                # Step 3: Try to create the same user again (should return status: false)
                logger.info("\n3️⃣ Attempting to create the same user again...")
                
                response2 = requests.post(
                    f"{base_url}/auth/create-user/patient",
                    json=test_user,
                    verify=False,
                    timeout=30
                )
                
                logger.info(f"Second creation - Status: {response2.status_code}")
                logger.info(f"Second creation - Response: {response2.text}")
                
                if response2.status_code == 200:
                    data2 = response2.json()
                    
                    if data2.get('status') is False:
                        logger.info("✅ Correctly returned status: false for duplicate user")
                        logger.info(f"✅ Message: {data2.get('message')}")
                        logger.info(f"✅ Redirect to reset: {data2.get('redirect_to_reset')}")
                        return True
                    else:
                        logger.error(f"❌ Expected status: false but got: {data2.get('status')}")
                        return False
                else:
                    logger.error(f"❌ Expected status 200 for duplicate user but got: {response2.status_code}")
                    return False
                    
            else:
                logger.error(f"❌ Verification failed: {verify_response.status_code}")
                return False
                
        else:
            logger.error(f"❌ First user creation failed: {response1.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error in duplicate user test: {str(e)}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return False

def main():
    """Run the duplicate user test."""
    logger.info("🚀 Starting Duplicate User Handling Test")
    
    success = test_duplicate_user_workflow()
    
    logger.info("\n" + "=" * 60)
    if success:
        logger.info("🎉 Duplicate User Handling Test PASSED!")
        logger.info("✅ The system correctly returns status: false for duplicate users")
    else:
        logger.info("❌ Duplicate User Handling Test FAILED!")
        logger.info("⚠️ The system is not handling duplicate users correctly")
    logger.info("=" * 60)

if __name__ == "__main__":
    main() 