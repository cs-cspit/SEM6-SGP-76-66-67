import smtplib
from email.message import EmailMessage
import threading
from database.db import db

class EmailSender:
    
    @staticmethod
    def send_absent_notification(receiver_email, student_name, subject, time_slot, date):
        def _send():
            try:
                config = db.get_email_config()
                sender_email = config.get("sender_email")
                app_password = config.get("app_password")

                if not sender_email or not app_password:
                    print("Email config missing. Cannot send absent email.")
                    return

                msg = EmailMessage()
                msg.set_content(f"Dear {student_name},\n\nYou were absent today ({date}) in {subject} class ({time_slot}).\n\nPlease ensure you attend future classes.\n\nRegards,\nSmart Attendance System")
                msg['Subject'] = f"Absence Notification: {subject}"
                msg['From'] = sender_email
                msg['To'] = receiver_email

                try:
                    # Try Port 587 (STARTTLS) first as it's more widely supported by edu/workspace accounts
                    server = smtplib.SMTP('smtp.gmail.com', 587)
                    server.starttls()
                    server.login(sender_email, app_password)
                    server.send_message(msg)
                    server.quit()
                    print(f"Absent email sent to {receiver_email} via Port 587")
                except Exception as e:
                    print(f"Port 587 failed ({e}), trying Port 465 (SSL)...")
                    # Fallback to Port 465 SSL
                    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                    server.login(sender_email, app_password)
                    server.send_message(msg)
                    server.quit()
                    print(f"Absent email sent to {receiver_email} via Port 465")
                    
            except smtplib.SMTPAuthenticationError:
                print(f"Failed to send email to {receiver_email}: Authentication Error! Make sure you are using a 16-character Google App Password, not your normal password. Also check if 2FA is enabled.")
            except Exception as e:
                print(f"Failed to send email to {receiver_email}: {e}")

        # Run in background to avoid blocking main thread
        threading.Thread(target=_send, daemon=True).start()

    @staticmethod
    def send_present_notification(receiver_email, student_name, subject, time_slot, date, time_marked):
        def _send():
            try:
                config = db.get_email_config()
                sender_email = config.get("sender_email")
                app_password = config.get("app_password")

                if not sender_email or not app_password:
                    return # Silent return if no config is set

                msg = EmailMessage()
                msg.set_content(f"Dear {student_name},\n\nYou have been marked PRESENT today ({date} at {time_marked}) for {subject} class ({time_slot}).\n\nRegards,\nSmart Attendance System")
                msg['Subject'] = f"Attendance Marked Present: {subject}"
                msg['From'] = sender_email
                msg['To'] = receiver_email

                try:
                    server = smtplib.SMTP('smtp.gmail.com', 587)
                    server.starttls()
                    server.login(sender_email, app_password)
                    server.send_message(msg)
                    server.quit()
                    print(f"Present email sent to {receiver_email} via Port 587")
                except Exception as e:
                    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                    server.login(sender_email, app_password)
                    server.send_message(msg)
                    server.quit()
                    print(f"Present email sent to {receiver_email} via Port 465")
                    
            except Exception as e:
                print(f"Failed to send present email to {receiver_email}: {e}")

        threading.Thread(target=_send, daemon=True).start()
