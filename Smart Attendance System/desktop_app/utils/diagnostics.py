import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.db import db
from datetime import datetime

def diagnostics():
    print("=== System Diagnostics ===")
    
    # 1. Check Email Config
    cfg = db.get_email_config()
    print(f"Email Sender: {cfg.get('sender_email')}")
    print(f"App Password Set: {bool(cfg.get('app_password'))}")
    
    # 2. Check Students
    students = db.get_all_students()
    print(f"\nTotal Registered Students: {len(students)}")
    for s in students:
        print(f" - ID: {s.get('student_id')}, Name: {s.get('name')}, Email: {s.get('email', 'MISSING!')}")
        
    # 3. Check Today's Attendance
    today = datetime.now().strftime("%Y-%m-%d")
    att = db.get_attendance_reports(today)
    print(f"\nToday's Attendance Records: {len(att)}")
    for a in att:
        print(f" - {a.get('name')} marked Present at {a.get('time')}")

if __name__ == "__main__":
    diagnostics()
