import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Email Configuration - UPDATE THESE WITH YOUR GMAIL CREDENTIALS
# For Gmail, you need to use an App Password (not your regular password)
# See instructions in EMAIL_SETUP.md
GMAIL_SENDER = "vishnu192004@gmail.com"  # Your Gmail address
GMAIL_APP_PASSWORD = "kbkyaqgqpvjytnih"  # Gmail App Password (16 characters, NO SPACES)

def sendmail(toemail, otp):
    """
    Send OTP email to user.
    Returns True if successful, False otherwise.
    """
    TO = toemail
    SUBJECT = 'E-Voting System - OTP Verification'
    TEXT = f"Your OTP for voting is: {otp}\n\nPlease enter this OTP to proceed with voting."
    
    print(f"Attempting to send OTP {otp} to {TO}")
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = GMAIL_SENDER
        msg['To'] = TO
        msg['Subject'] = SUBJECT
        msg.attach(MIMEText(TEXT, 'plain'))
        
        # Connect to Gmail SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.ehlo()
        
        # Login with App Password
        server.login(GMAIL_SENDER, GMAIL_APP_PASSWORD)
        
        # Send email
        text = msg.as_string()
        server.sendmail(GMAIL_SENDER, [TO], text)
        server.quit()
        
        print(f'[SUCCESS] Email sent successfully to {TO}')
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f'[ERROR] SMTP Authentication Error: {e}')
        print('Please check:')
        print('1. Gmail App Password is correct (not regular password)')
        print('2. App Password has NO SPACES (remove all spaces)')
        print('3. 2-Step Verification is enabled on your Google account')
        print('4. App Password is generated correctly')
        print(f'   Current password length: {len(GMAIL_APP_PASSWORD)} (should be 16)')
        return False
    except Exception as e:
        print(f'[ERROR] Error sending email: {e}')
        return False
