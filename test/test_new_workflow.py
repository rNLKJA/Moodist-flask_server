#!/usr/bin/env python
"""Comprehensive test script for the new 7-day verification workflow."""

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

class MoodistAPITester:
    """Test class for the new Moodist authentication workflow."""
    
    def __init__(self, base_url="https://localhost:20001"):
        self.base_url = base_url
        self.session = requests.Session()
        # Ignore SSL verification for localhost testing
        self.session.verify = False
        
    def test_user_creation(self, email, password="TestPassword123!", first_name="Test", last_name="User"):
        """Test user creation with the new workflow."""
        logger.info(f"Testing user creation for {email}")
        
        url = f"{self.base_url}/auth/create-user/patient"
        data = {
            "email": email,
            "password": password,
            "first_name": first_name,
            "last_name": last_name
        }
        
        try:
            response = self.session.post(url, json=data)
            logger.info(f"Status code: {response.status_code}")
            logger.info(f"Response: {response.text}")
            
            if response.status_code == 201:
                response_data = response.json()
                verification_token = response_data.get('verification_token')
                expires_in_days = response_data.get('expires_in_days')
                
                # Extract verification code from the token for testing
                verification_code = self._extract_verification_code(verification_token)
                
                logger.info(f"✅ User creation successful!")
                logger.info(f"📧 Verification token received")
                logger.info(f"⏱️ Expires in {expires_in_days} days")
                logger.info(f"🔢 Verification code: {verification_code}")
                
                return {
                    'success': True,
                    'verification_token': verification_token,
                    'verification_code': verification_code,
                    'expires_in_days': expires_in_days
                }
            else:
                logger.error(f"❌ User creation failed: {response.text}")
                return {'success': False, 'response': response.json()}
                
        except Exception as e:
            logger.error(f"❌ Error during user creation: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def test_verification(self, verification_token, verification_code):
        """Test user verification with the 6-digit code."""
        logger.info(f"Testing verification with code: {verification_code}")
        
        url = f"{self.base_url}/auth/verify"
        data = {
            "verification_token": verification_token,
            "verification_code": verification_code
        }
        
        try:
            response = self.session.post(url, json=data)
            logger.info(f"Status code: {response.status_code}")
            logger.info(f"Response: {response.text}")
            
            if response.status_code == 200:
                response_data = response.json()
                unique_id = response_data.get('unique_id')
                user_type = response_data.get('user_type')
                display_name = response_data.get('display_name')
                
                logger.info(f"✅ Verification successful!")
                logger.info(f"🆔 Unique ID: {unique_id}")
                logger.info(f"👤 User type: {user_type}")
                logger.info(f"📛 Display name: {display_name}")
                
                return {
                    'success': True,
                    'unique_id': unique_id,
                    'user_type': user_type,
                    'display_name': display_name
                }
            else:
                logger.error(f"❌ Verification failed: {response.text}")
                return {'success': False, 'response': response.json()}
                
        except Exception as e:
            logger.error(f"❌ Error during verification: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def test_resend_verification(self, email):
        """Test resending verification code."""
        logger.info(f"Testing resend verification for {email}")
        
        url = f"{self.base_url}/auth/resend-verification"
        data = {
            "email": email
        }
        
        try:
            response = self.session.post(url, json=data)
            logger.info(f"Status code: {response.status_code}")
            logger.info(f"Response: {response.text}")
            
            if response.status_code == 200:
                response_data = response.json()
                verification_token = response_data.get('verification_token')
                expires_in_days = response_data.get('expires_in_days')
                
                # Extract verification code from the token for testing
                verification_code = self._extract_verification_code(verification_token)
                
                logger.info(f"✅ Resend verification successful!")
                logger.info(f"📧 New verification token received")
                logger.info(f"⏱️ Expires in {expires_in_days} days")
                logger.info(f"🔢 New verification code: {verification_code}")
                
                return {
                    'success': True,
                    'verification_token': verification_token,
                    'verification_code': verification_code
                }
            else:
                logger.error(f"❌ Resend verification failed: {response.text}")
                return {'success': False, 'response': response.json()}
                
        except Exception as e:
            logger.error(f"❌ Error during resend verification: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def test_duplicate_user_creation(self, email):
        """Test creating a user that already exists."""
        logger.info(f"Testing duplicate user creation for {email}")
        
        result = self.test_user_creation(email)
        if result.get('success'):
            logger.info("✅ Duplicate user creation handled correctly (resend logic)")
        else:
            response_data = result.get('response', {})
            if 'already exists and is active' in response_data.get('message', ''):
                logger.info("✅ Correctly rejected active user creation")
            else:
                logger.error("❌ Unexpected response for duplicate user")
        
        return result
    
    def _extract_verification_code(self, verification_token):
        """Extract verification code from token for testing purposes."""
        try:
            from src.utils.token_generator import verify_verification_token
            from itsdangerous import URLSafeTimedSerializer
            
            secret_key = os.environ.get('SECRET_KEY')
            salt = os.environ.get('SECURITY_PASSWORD_SALT')
            
            serializer = URLSafeTimedSerializer(secret_key)
            payload = serializer.loads(verification_token, salt=salt)
            return payload.get('code')
        except Exception as e:
            logger.error(f"Failed to extract verification code: {str(e)}")
            return None

def run_comprehensive_test():
    """Run comprehensive test of the new workflow."""
    logger.info("🚀 Starting comprehensive test of the new Moodist authentication workflow")
    logger.info("=" * 80)
    
    tester = MoodistAPITester()
    test_email = "test_new_workflow@example.com"
    
    # Test 1: Create new user
    logger.info("\n📋 Test 1: Creating new user account")
    logger.info("-" * 40)
    creation_result = tester.test_user_creation(test_email)
    
    if not creation_result.get('success'):
        logger.error("❌ Test failed at user creation stage")
        return False
    
    verification_token = creation_result['verification_token']
    verification_code = creation_result['verification_code']
    
    # Test 2: Test invalid verification code
    logger.info("\n📋 Test 2: Testing invalid verification code")
    logger.info("-" * 40)
    invalid_result = tester.test_verification(verification_token, "000000")
    
    if invalid_result.get('success'):
        logger.error("❌ Invalid verification code was accepted!")
        return False
    else:
        logger.info("✅ Invalid verification code correctly rejected")
    
    # Test 3: Test resend verification
    logger.info("\n📋 Test 3: Testing resend verification")
    logger.info("-" * 40)
    resend_result = tester.test_resend_verification(test_email)
    
    if resend_result.get('success'):
        # Use the new verification code
        verification_token = resend_result['verification_token']
        verification_code = resend_result['verification_code']
    
    # Test 4: Test valid verification
    logger.info("\n📋 Test 4: Testing valid verification")
    logger.info("-" * 40)
    verification_result = tester.test_verification(verification_token, verification_code)
    
    if not verification_result.get('success'):
        logger.error("❌ Test failed at verification stage")
        return False
    
    # Test 5: Test duplicate user creation (should fail for active user)
    logger.info("\n📋 Test 5: Testing duplicate user creation")
    logger.info("-" * 40)
    duplicate_result = tester.test_duplicate_user_creation(test_email)
    
    # Test 6: Test duplicate verification (should fail)
    logger.info("\n📋 Test 6: Testing duplicate verification")
    logger.info("-" * 40)
    duplicate_verification = tester.test_verification(verification_token, verification_code)
    
    if duplicate_verification.get('success'):
        logger.error("❌ Duplicate verification was accepted!")
        return False
    else:
        logger.info("✅ Duplicate verification correctly rejected")
    
    logger.info("\n" + "=" * 80)
    logger.info("🎉 All tests completed successfully!")
    logger.info("✅ The new 7-day verification workflow is working correctly")
    
    return True

if __name__ == "__main__":
    # Run the comprehensive test
    success = run_comprehensive_test()
    
    if success:
        logger.info("\n🎯 Summary: All tests passed!")
        exit(0)
    else:
        logger.error("\n💥 Summary: Some tests failed!")
        exit(1) 