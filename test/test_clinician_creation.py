#!/usr/bin/env python
"""Test script to verify the complete clinician account creation and management flow."""

import os
import json
import requests
from dotenv import load_dotenv
import logging
import time

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

# Base URL for the API
BASE_URL = "https://localhost:20001"

def test_clinician_creation():
    """Test the clinician account creation endpoint."""
    logger.info("Testing clinician account creation endpoint...")
    
    # Define the test clinician data
    test_clinician = {
        "email": "dr.test@unimelb.edu.au",
        "password": "SecureClinicianPassword123!"
    }
    
    # Define the API endpoint
    url = f"{BASE_URL}/auth/create-clinician"
    
    try:
        # Make the API request (ignoring SSL verification for localhost)
        response = requests.post(url, json=test_clinician, verify=False)
        
        # Print the response
        logger.info(f"Status code: {response.status_code}")
        logger.info(f"Response: {response.text}")
        
        # Check if the request was successful
        if response.status_code == 201:
            response_data = response.json()
            logger.info("Clinician account creation successful!")
            logger.info(f"Token expires: {response_data.get('expires_at')}")
            return response_data
        else:
            logger.error(f"Clinician creation failed with status code: {response.status_code}")
            return None
            
    except Exception as e:
        logger.error(f"Error making API request: {str(e)}")
        return None

def test_clinician_login():
    """Test clinician login (after verification)."""
    logger.info("Testing clinician login...")
    
    login_data = {
        "email": "dr.test@unimelb.edu.au",
        "password": "SecureClinicianPassword123!",
        "user_type": "doctor"
    }
    
    url = f"{BASE_URL}/auth/login"
    
    try:
        response = requests.post(url, json=login_data, verify=False)
        logger.info(f"Login Status code: {response.status_code}")
        logger.info(f"Login Response: {response.text}")
        
        if response.status_code == 200:
            logger.info("Clinician login successful!")
            return response.json()
        else:
            logger.info("Clinician login failed (expected if not verified)")
            return None
            
    except Exception as e:
        logger.error(f"Error in clinician login: {str(e)}")
        return None

def test_clinician_password_reset():
    """Test clinician password reset functionality."""
    logger.info("Testing clinician password reset...")
    
    # Step 1: Request password reset
    reset_request_data = {
        "email": "dr.test@unimelb.edu.au"
    }
    
    url = f"{BASE_URL}/auth/clinician/request-password-reset"
    
    try:
        response = requests.post(url, json=reset_request_data, verify=False)
        logger.info(f"Password reset request status: {response.status_code}")
        logger.info(f"Password reset request response: {response.text}")
        
        if response.status_code == 200:
            logger.info("Password reset code requested successfully!")
            
            # Note: In a real scenario, you would get the code from email
            # For testing, you'd need to manually extract it from the database
            logger.info("Check the clinician's email for the reset code")
            logger.info("In production, you would complete the reset using the code from email")
            
            return True
        else:
            logger.error("Password reset request failed")
            return False
            
    except Exception as e:
        logger.error(f"Error in password reset request: {str(e)}")
        return False

def test_generic_doctor_creation():
    """Test the generic doctor account creation endpoint."""
    logger.info("Testing generic doctor account creation (should also work for clinicians)...")
    
    test_doctor = {
        "email": "dr.generic@unimelb.edu.au",
        "password": "GenericDoctorPassword123!"
    }
    
    url = f"{BASE_URL}/auth/create-user/doctor"
    
    try:
        response = requests.post(url, json=test_doctor, verify=False)
        logger.info(f"Generic doctor creation status: {response.status_code}")
        logger.info(f"Generic doctor creation response: {response.text}")
        
        if response.status_code == 201:
            logger.info("Generic doctor account creation successful!")
            return response.json()
        else:
            logger.error("Generic doctor creation failed")
            return None
            
    except Exception as e:
        logger.error(f"Error in generic doctor creation: {str(e)}")
        return None

def main():
    """Run all clinician tests."""
    logger.info("Starting Clinician Account Tests")
    logger.info("=" * 50)
    
    # Test 1: Create clinician with enhanced data
    logger.info("Test 1: Enhanced Clinician Creation")
    creation_result = test_clinician_creation()
    
    time.sleep(2)  # Small delay between tests
    
    # Test 2: Test login (will fail if not verified)
    logger.info("\nTest 2: Clinician Login (before verification)")
    login_result = test_clinician_login()
    
    time.sleep(2)
    
    # Test 3: Test password reset
    logger.info("\nTest 3: Clinician Password Reset")
    reset_result = test_clinician_password_reset()
    
    time.sleep(2)
    
    # Test 4: Test generic doctor creation
    logger.info("\nTest 4: Generic Doctor Creation")
    generic_result = test_generic_doctor_creation()
    
    # Summary
    logger.info("\n" + "=" * 50)
    logger.info("TEST SUMMARY:")
    logger.info(f"Enhanced Clinician Creation: {'PASS' if creation_result else 'FAIL'}")
    logger.info(f"Clinician Login (unverified): {'EXPECTED FAIL' if not login_result else 'UNEXPECTED PASS'}")
    logger.info(f"Password Reset Request: {'PASS' if reset_result else 'FAIL'}")
    logger.info(f"Generic Doctor Creation: {'PASS' if generic_result else 'FAIL'}")
    
    if creation_result:
        logger.info("\nIMPORTANT:")
        logger.info("- Check the email dr.test@unimelb.edu.au for verification link")
        logger.info("- After verification, login should work")

# run the main function
if __name__ == "__main__":
    main()    