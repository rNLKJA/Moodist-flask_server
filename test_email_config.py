#!/usr/bin/env python
"""Test script to verify email configuration is working."""

import logging
import os

from dotenv import load_dotenv

from src.utils.email_sender import send_email, validate_email_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_email_config():
    """Test the email configuration and send a test email."""

    print("=" * 60)
    print("MOODIST EMAIL CONFIGURATION TEST")
    print("=" * 60)

    # Load environment variables
    load_dotenv()

    # Validate configuration
    config_status = validate_email_config()

    print("\n📧 Email Configuration Status:")
    print(f"EMAIL_HOST: {os.environ.get('EMAIL_HOST', 'NOT SET')}")
    print(f"EMAIL_HOST_USER: {os.environ.get('EMAIL_HOST_USER', 'NOT SET')}")
    print(
        f"EMAIL_HOST_PASSWORD: {'***' + os.environ.get('EMAIL_HOST_PASSWORD', '')[-4:] if os.environ.get('EMAIL_HOST_PASSWORD') else 'NOT SET'}"
    )
    print(f"EMAIL_PORT: {os.environ.get('EMAIL_PORT', 'NOT SET')}")
    print(f"EMAIL_USE_SSL: {os.environ.get('EMAIL_USE_SSL', 'NOT SET')}")

    password = os.environ.get("EMAIL_HOST_PASSWORD", "")
    if password:
        clean_password = password.strip("\"'")
        print(f"Password length: {len(clean_password)} characters")
        if len(clean_password) == 16:
            print("✅ Password length is correct for Gmail App Password")
        else:
            print("❌ Password length incorrect for Gmail App Password (should be 16)")

    print(
        f"\n🔍 Configuration Valid: {'✅ YES' if config_status['valid'] else '❌ NO'}"
    )

    if config_status["issues"]:
        print("\n❌ Issues found:")
        for issue in config_status["issues"]:
            print(f"  - {issue}")

    if config_status["recommendations"]:
        print("\n💡 Recommendations:")
        for rec in config_status["recommendations"]:
            print(f"  - {rec}")

    # Test email sending if configuration looks good
    if config_status["valid"] and len(clean_password) == 16:
        test_email = input(
            "\n📧 Enter email address to send test email (or press Enter to skip): "
        ).strip()

        if test_email:
            print(f"\n📤 Sending test email to {test_email}...")

            test_subject = "Moodist Email Configuration Test"
            test_body = """
            <html>
                <body style="font-family: Arial, sans-serif;">
                    <h2>✅ Email Configuration Test Successful!</h2>
                    <p>This is a test email from your Moodist Flask server.</p>
                    <p>Your email configuration is working correctly!</p>
                    <hr>
                    <p style="color: #666; font-size: 14px;">
                        Sent from Moodist Platform<br>
                        University of Melbourne
                    </p>
                </body>
            </html>
            """

            success = send_email(test_email, test_subject, test_body)

            if success:
                print("✅ Test email sent successfully!")
                print("🎉 Your email configuration is working!")
            else:
                print("❌ Test email failed to send. Check the logs above for details.")
        else:
            print("⏭️ Skipping test email send.")
    else:
        print("\n⚠️ Cannot test email sending due to configuration issues.")
        print("Please fix the issues above and run this test again.")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    test_email_config()
