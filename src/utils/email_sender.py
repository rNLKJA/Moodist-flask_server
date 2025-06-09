"""Email sender utility with improved Gmail App Password support."""

import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr

# Configure logger
logger = logging.getLogger(__name__)

def send_email(to_email, subject, template):
    """
    Send an email using the configured SMTP server.
    
    For Gmail SMTP, you MUST use an App Password, not your regular Gmail password.
    
    To generate a Gmail App Password:
    1. Go to Google Account settings (myaccount.google.com)
    2. Select Security > 2-Step Verification (must be enabled)
    3. Select App passwords
    4. Generate a new app password for "Mail"
    5. Use that 16-character password (no spaces) in EMAIL_HOST_PASSWORD
    
    Args:
        to_email (str): Recipient email address
        subject (str): Email subject
        template (str): HTML content of the email
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    # Get email configuration from environment variables
    email_host = os.environ.get('EMAIL_HOST')
    email_port = int(os.environ.get('EMAIL_PORT', 465))
    email_user = os.environ.get('EMAIL_HOST_USER')
    email_password = os.environ.get('EMAIL_HOST_PASSWORD')
    email_use_ssl = os.environ.get('EMAIL_USE_SSL', 'True').lower() == 'true'
    
    # Check if all required email settings are available
    if not all([email_host, email_user, email_password]):
        logger.error("Email configuration is incomplete. Check environment variables.")
        logger.error("Required: EMAIL_HOST, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD")
        return False
    
    # Remove quotes from password if present
    if email_password.startswith('"') and email_password.endswith('"'):
        email_password = email_password[1:-1]
    
    try:
        # Create message container
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        # Format the "From" header to show "Moodist Team" instead of the actual email
        msg['From'] = formataddr(("Moodist Team", email_user))
        msg['To'] = to_email
        
        # Attach HTML content
        html_part = MIMEText(template, 'html')
        msg.attach(html_part)
        
        # Connect to server and send email
        if email_use_ssl:
            server = smtplib.SMTP_SSL(email_host, email_port)
        else:
            server = smtplib.SMTP(email_host, email_port)
            server.starttls()
        
        # Enable debug output for troubleshooting
        server.set_debuglevel(0)  # Set to 1 for detailed SMTP debugging
        
        server.login(email_user, email_password)
        server.sendmail(email_user, to_email, msg.as_string())
        server.quit()
        
        logger.info(f"Verification email sent successfully to {to_email}")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        if "Username and Password not accepted" in str(e):
            logger.error("Gmail authentication failed - App Password required!")
            logger.error("=" * 60)
            logger.error("GMAIL APP PASSWORD SETUP INSTRUCTIONS:")
            logger.error("1. Go to myaccount.google.com")
            logger.error("2. Security > 2-Step Verification (must be enabled first)")
            logger.error("3. Security > App passwords")
            logger.error("4. Generate app password for 'Mail'")
            logger.error("5. Use the 16-character password (no spaces) in EMAIL_HOST_PASSWORD")
            logger.error("6. Example: EMAIL_HOST_PASSWORD=abcdabcdabcdabcd")
            logger.error("=" * 60)
            logger.error(f"Current password length: {len(email_password)} characters")
            logger.error(f"Expected App Password length: 16 characters")
        else:
            logger.error(f"SMTP Authentication error: {str(e)}")
        return False
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error occurred: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        return False

def validate_email_config():
    """
    Validate email configuration and provide helpful messages.
    
    Returns:
        dict: Configuration status and recommendations
    """
    config = {
        'valid': True,
        'issues': [],
        'recommendations': []
    }
    
    email_host = os.environ.get('EMAIL_HOST')
    email_user = os.environ.get('EMAIL_HOST_USER')
    email_password = os.environ.get('EMAIL_HOST_PASSWORD')
    
    if not email_host:
        config['valid'] = False
        config['issues'].append('EMAIL_HOST not set')
        
    if not email_user:
        config['valid'] = False
        config['issues'].append('EMAIL_HOST_USER not set')
        
    if not email_password:
        config['valid'] = False
        config['issues'].append('EMAIL_HOST_PASSWORD not set')
    else:
        # Remove quotes for validation
        clean_password = email_password.strip('"\'')
        
        if email_host == 'smtp.gmail.com':
            if len(clean_password) != 16:
                config['issues'].append(f'Gmail App Password should be 16 characters, got {len(clean_password)}')
                config['recommendations'].append('Generate a Gmail App Password')
            
            if ' ' in clean_password:
                config['issues'].append('Gmail App Password should not contain spaces')
                config['recommendations'].append('Remove spaces from App Password')
                
            if clean_password == email_user.split('@')[0]:  # Password same as username
                config['issues'].append('Using Gmail account password instead of App Password')
                config['recommendations'].append('Generate and use Gmail App Password')
    
    return config 