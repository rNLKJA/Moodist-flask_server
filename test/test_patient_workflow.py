#!/usr/bin/env python
"""Test script for patient database workflow with improved error handling."""

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

def test_patient_creation():
    """Test patient creation in the patient database."""
    base_url = "https://localhost:20001"
    test_email = "patient_test@example.com"
    
    logger.info("=" * 60)
    logger.info("🏥 Testing Patient Account Creation")
    logger.info("=" * 60)
    
    # Test patient creation
    logger.info("📋 Creating patient account...")
    create_url = f"{base_url}/auth/create-user/patient"
    create_data = {
        "email": test_email,
        "password": "jumpingJelly81**",  # Using user's preferred password format
        "first_name": "Test",
        "last_name": "Patient"
    }
    
    try:
        response = requests.post(create_url, json=create_data, verify=False)
        logger.info(f"📊 Status code: {response.status_code}")
        
        if response.status_code == 201:
            response_data = response.json()
            logger.info("✅ Patient creation successful!")
            logger.info(f"🏗️  Database: {response_data.get('database', 'Unknown')}")
            logger.info(f"👤 User type: {response_data.get('user_type', 'Unknown')}")
            logger.info(f"📧 Email sent: {response_data.get('email_sent', False)}")
            logger.info(f"⏰ Expires in: {response_data.get('expires_in_days', 'Unknown')} days")
            
            # Extract verification code from token
            verification_token = response_data.get('verification_token')
            verification_code = extract_verification_code(verification_token)
            
            if verification_code:
                logger.info(f"🔢 Verification code: {verification_code}")
                
                # Test verification
                logger.info("\n📋 Testing verification...")
                verify_result = test_verification(base_url, verification_token, verification_code)
                
                if verify_result:
                    logger.info("🎉 Full patient workflow completed successfully!")
                    return True
                else:
                    logger.error("❌ Verification failed")
                    return False
            else:
                logger.error("❌ Could not extract verification code")
                return False
                
        elif response.status_code == 200:
            # This is the forgot password scenario
            response_data = response.json()
            if response_data.get('status') == 'info':
                logger.info("ℹ️ Account already exists - forgot password email sent")
                logger.info(f"📝 Message: {response_data.get('message')}")
                return True
        else:
            logger.error(f"❌ Patient creation failed")
            logger.error(f"📝 Response: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error during patient creation: {str(e)}")
        return False

def test_verification(base_url, verification_token, verification_code):
    """Test verification process."""
    verify_url = f"{base_url}/auth/verify"
    verify_data = {
        "verification_token": verification_token,
        "verification_code": verification_code
    }
    
    try:
        response = requests.post(verify_url, json=verify_data, verify=False)
        logger.info(f"📊 Verification status code: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            logger.info("✅ Verification successful!")
            logger.info(f"🆔 Unique ID: {response_data.get('unique_id')}")
            logger.info(f"🏗️  Database: {response_data.get('database')}")
            logger.info(f"👤 User type: {response_data.get('user_type')}")
            logger.info(f"📛 Display name: {response_data.get('display_name')}")
            return True
        else:
            logger.error(f"❌ Verification failed: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error during verification: {str(e)}")
        return False

def test_duplicate_patient():
    """Test duplicate patient creation (should send forgot password email)."""
    base_url = "https://localhost:20001"
    test_email = "patient_test@example.com"  # Same email as above
    
    logger.info("\n" + "=" * 60)
    logger.info("🔄 Testing Duplicate Patient Creation")
    logger.info("=" * 60)
    
    create_url = f"{base_url}/auth/create-user/patient"
    create_data = {
        "email": test_email,
        "password": "newPassword123!",
        "first_name": "Duplicate",
        "last_name": "Patient"
    }
    
    try:
        response = requests.post(create_url, json=create_data, verify=False)
        logger.info(f"📊 Status code: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            if response_data.get('status') == 'info':
                logger.info("✅ Correct behavior: Forgot password email sent for existing account")
                logger.info(f"📝 Message: {response_data.get('message')}")
                return True
        else:
            logger.error(f"❌ Unexpected response for duplicate patient")
            logger.error(f"📝 Response: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error during duplicate patient test: {str(e)}")
        return False

def extract_verification_code(verification_token):
    """Extract verification code from token for testing."""
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

def test_email_configuration():
    """Test email configuration validation."""
    logger.info("\n" + "=" * 60)
    logger.info("📧 Testing Email Configuration")
    logger.info("=" * 60)
    
    try:
        from src.utils.email_sender import validate_email_config
        
        config = validate_email_config()
        
        if config['valid']:
            logger.info("✅ Email configuration is valid")
        else:
            logger.warning("⚠️ Email configuration issues found:")
            for issue in config['issues']:
                logger.warning(f"   - {issue}")
                
            if config['recommendations']:
                logger.info("💡 Recommendations:")
                for rec in config['recommendations']:
                    logger.info(f"   - {rec}")
        
        return config['valid']
        
    except Exception as e:
        logger.error(f"❌ Error validating email config: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("🚀 Starting Patient Database Workflow Test")
    
    # Test email configuration first
    email_valid = test_email_configuration()
    
    # Test patient creation
    patient_result = test_patient_creation()
    
    # Test duplicate handling
    duplicate_result = test_duplicate_patient()
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 TEST SUMMARY")
    logger.info("=" * 60)
    logger.info(f"📧 Email Config: {'✅ Valid' if email_valid else '⚠️ Issues'}")
    logger.info(f"🏥 Patient Creation: {'✅ Success' if patient_result else '❌ Failed'}")
    logger.info(f"🔄 Duplicate Handling: {'✅ Success' if duplicate_result else '❌ Failed'}")
    
    if patient_result and duplicate_result:
        logger.info("\n🎉 All patient workflow tests passed!")
        if not email_valid:
            logger.warning("⚠️ Note: Email configuration needs attention for production use")
        exit(0)
    else:
        logger.error("\n💥 Some tests failed!")
        exit(1) 