"""Email templates for verification emails with 7-day expiry support."""

def get_verification_email_template(verification_code, verification_link=None):
    """
    Get HTML template for verification email with 7-day expiry.
    
    Args:
        verification_code (str): 6-digit verification code
        verification_link (str, optional): Direct verification link
        
    Returns:
        str: HTML email template
    """
    verification_section = ""
    if verification_link:
        verification_section = f"""
        <div style="text-align: center; margin: 30px 0;">
            <a href="{verification_link}" 
               style="background-color: #2D3142; color: white; padding: 15px 30px; 
                      text-decoration: none; border-radius: 5px; font-weight: bold; 
                      display: inline-block; font-size: 16px;">
                Verify My Account
            </a>
        </div>
        <p style="text-align: center; margin: 20px 0; color: #666;">
            Or enter this verification code manually:
        </p>
        """
    else:
        verification_section = """
        <p>Please use the verification code below to complete your registration:</p>
        """
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Verify Your Moodist Account</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333333;
                margin: 0;
                padding: 0;
                background-color: #f5f5f5;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                background-color: #ffffff;
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }}
            .header {{
                background: linear-gradient(135deg, #B6D8C7 0%, #8FB3A9 100%);
                padding: 30px 20px;
                text-align: center;
                color: white;
            }}
            .header h1 {{
                margin: 0;
                font-size: 28px;
                font-weight: 300;
                letter-spacing: 2px;
            }}
            .content {{
                padding: 40px 30px;
                background-color: #ffffff;
            }}
            .verification-code {{
                font-size: 32px;
                font-weight: bold;
                text-align: center;
                margin: 30px 0;
                padding: 20px;
                background-color: #f8f9fa;
                border-radius: 10px;
                letter-spacing: 8px;
                border: 2px solid #8FB3A9;
                color: #2D3142;
            }}
            .info-box {{
                background-color: #e8f1f2;
                border-left: 4px solid #8FB3A9;
                padding: 15px 20px;
                margin: 25px 0;
                border-radius: 5px;
            }}
            .warning-box {{
                background-color: #fff3cd;
                border-left: 4px solid #ffc107;
                padding: 15px 20px;
                margin: 25px 0;
                border-radius: 5px;
            }}
            .footer {{
                text-align: center;
                padding: 30px 20px;
                font-size: 14px;
                color: #666666;
                background-color: #f8f9fa;
            }}
            .footer a {{
                color: #8FB3A9;
                text-decoration: none;
            }}
            .btn {{
                display: inline-block;
                padding: 15px 30px;
                background-color: #2D3142;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 16px;
                text-align: center;
            }}
            .btn:hover {{
                background-color: #1D2132;
            }}
            .logo-container {{
                display: flex;
                justify-content: center;
                margin-bottom: 15px;
            }}
            .unimelb-logo {{
                max-height: 50px;
                margin-top: 20px;
            }}
            @media only screen and (max-width: 600px) {{
                .container {{
                    margin: 10px;
                    border-radius: 5px;
                }}
                .content {{
                    padding: 30px 20px;
                }}
                .verification-code {{
                    font-size: 28px;
                    letter-spacing: 5px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>MOODIST</h1>
                <p style="margin: 10px 0 0 0; font-size: 16px; opacity: 0.9;">
                    Mental Health & Wellness Platform
                </p>
            </div>
            <div class="content">
                <div class="logo-container">
                    <img class="unimelb-logo" src="https://upload.wikimedia.org/wikipedia/en/thumb/a/ab/The_University_of_Melbourne_Logo.png/250px-The_University_of_Melbourne_Logo.png" alt="University of Melbourne">
                </div>
                
                <h2 style="color: #2D3142; margin-bottom: 20px; text-align: center;">Welcome to Moodist!</h2>
                
                <p>Thank you for joining our mental health and wellness community. We're excited to have you on board!</p>
                
                {verification_section}
                
                <div class="verification-code">{verification_code}</div>
                
                <div class="info-box">
                    <h4 style="margin: 0 0 10px 0; color: #2D3142;">⏰ Important Information:</h4>
                    <ul style="margin: 0; padding-left: 20px;">
                        <li><strong>This verification code expires in 7 days</strong></li>
                        <li>You have up to 5 attempts to enter the correct code</li>
                        <li>The code is case-sensitive and must be entered exactly as shown</li>
                    </ul>
                </div>
                
                <div class="warning-box">
                    <h4 style="margin: 0 0 10px 0; color: #856404;">🔒 Security Notice:</h4>
                    <p style="margin: 0;">
                        If you didn't create a Moodist account, please ignore this email. 
                        Your email address will be removed from our system automatically after 7 days.
                    </p>
                </div>
                
                <p style="margin-top: 30px;">
                    Once verified, you'll have access to:
                </p>
                <ul style="color: #666;">
                    <li>Personalized mood tracking tools</li>
                    <li>Professional mental health resources</li>
                    <li>Secure communication with healthcare providers</li>
                    <li>Evidence-based wellness programs</li>
                </ul>
                
                <p style="margin-top: 30px;">
                    Best regards,<br>
                    <strong>The Moodist Team</strong><br>
                    <small>University of Melbourne - Psychiatry Department</small>
                </p>
            </div>
            <div class="footer">
                <p>
                    This is an automated message, please do not reply to this email.<br>
                    If you need assistance, please contact our support team.
                </p>
                <p style="margin-top: 20px;">
                    &copy; {datetime.now().year} Moodist - University of Melbourne. All rights reserved.<br>
                    <a href="#" style="color: #8FB3A9;">Privacy Policy</a> | 
                    <a href="#" style="color: #8FB3A9;">Terms of Service</a> | 
                    <a href="#" style="color: #8FB3A9;">Support</a>
                </p>
            </div>
        </div>
    </body>
    </html>
    """

def get_verification_success_template(user_name=None):
    """
    Get HTML template for successful verification email.
    
    Args:
        user_name (str, optional): User's display name
        
    Returns:
        str: HTML email template
    """
    greeting = f"Hello {user_name}!" if user_name else "Hello!"
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Welcome to Moodist - Account Verified!</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333333;
                margin: 0;
                padding: 0;
                background-color: #f5f5f5;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                background-color: #ffffff;
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }}
            .header {{
                background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
                padding: 30px 20px;
                text-align: center;
                color: white;
            }}
            .content {{
                padding: 40px 30px;
            }}
            .success-icon {{
                text-align: center;
                font-size: 60px;
                margin: 20px 0;
            }}
            .btn {{
                display: inline-block;
                padding: 15px 30px;
                background-color: #28a745;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                font-weight: bold;
                text-align: center;
                margin: 20px 0;
            }}
            .footer {{
                text-align: center;
                padding: 30px 20px;
                font-size: 14px;
                color: #666666;
                background-color: #f8f9fa;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🧠 Moodist</h1>
                <p>Account Successfully Verified!</p>
            </div>
            <div class="content">
                <div class="success-icon">✅</div>
                
                <h2 style="color: #28a745; text-align: center;">Welcome to Moodist!</h2>
                
                <p>{greeting}</p>
                
                <p>Congratulations! Your Moodist account has been successfully verified and activated. 
                   You now have full access to our mental health and wellness platform.</p>
                
                <div style="text-align: center;">
                    <a href="#" class="btn">Access Your Dashboard</a>
                </div>
                
                <p>What's next? You can now:</p>
                <ul>
                    <li>Complete your profile setup</li>
                    <li>Start tracking your mood and wellness</li>
                    <li>Connect with healthcare providers</li>
                    <li>Explore our resources and tools</li>
                </ul>
                
                <p>If you have any questions or need assistance, our support team is here to help.</p>
                
                <p>
                    Best regards,<br>
                    <strong>The Moodist Team</strong>
                </p>
            </div>
            <div class="footer">
                <p>&copy; {datetime.now().year} Moodist - University of Melbourne. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """

# Import datetime for template usage
from datetime import datetime 