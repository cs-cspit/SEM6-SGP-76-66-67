import os
import sys

# Setup Path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.db import db
import smtplib
from email.message import EmailMessage

def test_email():
    print("Testing Email Sender...")
    
    config = db.get_email_config()
    sender_email = config.get("sender_email")
    app_password = config.get("app_password")

    print(f"Sender Email configured: '{sender_email}'")
    print(f"App Password configured: {'YES (Hidden)' if app_password else 'NO'}")
    
    if not sender_email or not app_password:
        print("FAIL: Cannot test email without configuration. Go to 'Attendance Control' and add credentials.")
        return

    receiver_email = sender_email # Send to self for test
    print(f"Attempting to send test email to {receiver_email} via smtp.gmail.com:465 (SSL)")

    try:
        msg = EmailMessage()
        msg.set_content(f"This is a test email from the Smart Attendance System.")
        msg['Subject'] = f"Test Email"
        msg['From'] = sender_email
        msg['To'] = receiver_email

        try:
            print("Trying Port 587 (STARTTLS)...")
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.set_debuglevel(0) # minimal debug
            server.starttls()
            server.login(sender_email, app_password)
            server.send_message(msg)
            server.quit()
            print("\n[SUCCESS] Test Email sent successfully via Port 587!")
        except Exception as e:
            print(f"Port 587 failed: {e}. Trying Port 465 (SSL)...")
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.set_debuglevel(0)
            server.login(sender_email, app_password)
            server.send_message(msg)
            server.quit()
            print("\n[SUCCESS] Test Email sent successfully via Port 465!")
            
    except smtplib.SMTPAuthenticationError:
        print("\n[FAIL] SMTP Authentication Error!")
        print("➤ The password you entered is incorrect OR blocked by Google.")
        print("➤ Google DOES NOT ALLOW your regular login password here.")
        print("➤ FIX: Go to https://myaccount.google.com/apppasswords and generate a 16-character App Password.")
        print("➤ NOTE: If your university (charusat.edu.in) has App Passwords disabled, you MUST use a personal @gmail.com account instead.")
    except Exception as e:
        print(f"\n[FAIL] Unexpected Error: {type(e).__name__} - {e}")

if __name__ == "__main__":
    test_email()
