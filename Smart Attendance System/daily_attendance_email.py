import smtplib
from email.message import EmailMessage
import schedule
import time
from datetime import datetime
import pymongo

# ==========================================
# Configuration Area
# ==========================================

# 1. Email configuration
SENDER_EMAIL = "23cs076@charusat.edu.in"
APP_PASSWORD = "sztq yqsd vlxn npur"

# 2. Daily Time for sending emails (24-hour format)
SCHEDULE_TIME = "18:00"  # 6:00 PM

# 3. Database configuration
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "smart_attendance_db"
# ==========================================


def send_email(server, student_name, receiver_email, date_str, status, subject=None):
    """
    Sends an attendance email to a single student using an existing SMTP server connection.
    """
    try:
        msg = EmailMessage()
        
        # Format the body
        body = f"""Hello {student_name},

This is your attendance report for today.

Date: {date_str}
Status: {status}
"""
        if subject:
            body += f"Subject/Class: {subject}\n"

        body += """
If you believe this is incorrect, please contact the administration.

Thank you."""
        
        msg.set_content(body)
        msg['Subject'] = "Daily Attendance Report"
        msg['From'] = SENDER_EMAIL
        msg['To'] = receiver_email

        # Send using the existing connection
        server.send_message(msg)
        
        print(f"[SUCCESS] Email sent to {student_name} ({receiver_email}) for status: {status}")
        
    except smtplib.SMTPAuthenticationError:
        print(f"[ERROR] Authentication failed for {SENDER_EMAIL}. Check if your App Password is correct and 2FA is enabled.")
    except Exception as e:
        print(f"[ERROR] Failed to send email to {receiver_email}. Reason: {e}")


def process_attendance_and_send_emails():
    """
    Reads the attendance from MongoDB for today's date and sends emails to all registered students.
    """
    print(f"\n--- Starting Daily Attendance Email Job at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
    
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    try:
        # Connect to Database
        client = pymongo.MongoClient(MONGO_URI)
        db = client[DB_NAME]
        students_collection = db["students"]
        attendance_collection = db["attendance"]

        # Fetch all registered students
        all_students = list(students_collection.find({}))
        if not all_students:
            print("[WARNING] No students found in the database. Nothing to send.")
            return

        emails_sent = 0
        
        # Connect to Gmail's SMTP server once for all emails
        print("Connecting to SMTP server...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, APP_PASSWORD)
        print("SMTP server connected.")
        
        for student in all_students:
            student_id = student.get("student_id")
            student_name = student.get("name")
            email_id = student.get("email")

            if not email_id:
                print(f"[WARNING] No email ID found for student: {student_name} ({student_id})")
                continue

            # Find all attendance records for this student today
            attendance_records = list(attendance_collection.find({
                "student_id": student_id,
                "date": today_str
            }))

            if attendance_records:
                # Student was present
                # They might have multiple records if they attended multiple subjects
                for record in attendance_records:
                    subject = record.get("subject", "General")
                    send_email(server, student_name, email_id, today_str, "Present", subject)
                    emails_sent += 1
                    time.sleep(1) # Small delay to avoid Gmail rate limit
            else:
                # Student was absent
                send_email(server, student_name, email_id, today_str, "Absent")
                emails_sent += 1
                time.sleep(1)

        server.quit()
        print(f"--- Finished Job. Total emails sent: {emails_sent} ---")
            
    except Exception as e:
        print(f"[ERROR] An unexpected error occurred: {e}")


def start_scheduler():
    """
    Sets up the daily schedule and runs the loop continuously.
    """
    print(f"Scheduler started. Emails will be sent every day at {SCHEDULE_TIME}.")
    print("Press Ctrl+C to stop.")
    
    # Schedule the job
    schedule.every().day.at(SCHEDULE_TIME).do(process_attendance_and_send_emails)

    # Keep the script running to check the schedule
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check the schedule every 60 seconds


if __name__ == "__main__":
    # =========================================================================
    # UNCOMMENT the line below to test the email sending IMMEDIATELY once.
    # process_attendance_and_send_emails()
    # =========================================================================
    
    # Start the continuous daily schedule
    start_scheduler()
