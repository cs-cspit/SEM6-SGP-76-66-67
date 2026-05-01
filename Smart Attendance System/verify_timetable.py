import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'desktop_app')))

# Mock database connection if needed, but we are running in the environment so legitimate connection should work if DB is running.
# Assuming DB is running as per user context.

try:
    from database.db import Database
    from datetime import datetime, timedelta

    db = Database()

    # 1. Add Timetable Entry for NOW
    now = datetime.now()
    day = now.strftime("%A")
    # Make sure we cover the current time
    start_time = (now - timedelta(minutes=5)).strftime("%H:%M")
    end_time = (now + timedelta(minutes=5)).strftime("%H:%M")
    subject = "TEST_SUBJECT_VERIFY"

    print(f"Adding class: {day} {start_time}-{end_time} {subject}")
    db.add_timetable_entry(day, start_time, end_time, subject)

    # 2. Check Active Class
    print("Checking active class...")
    active = db.get_active_class()
    if active and active['subject'] == subject:
        print("SUCCESS: Active class detected correctly.")
    else:
        print(f"FAILURE: Active class not detected. Got: {active}")

    # 3. Mark Attendance
    sid = "TEST_STUDENT_001"
    name = "Test Student"
    time_slot = f"{start_time}-{end_time}"
    success, msg = db.mark_attendance(sid, name, subject, time_slot)
    print(f"Mark Attendance 1: {success}, {msg}")

    # 4. Mark Again (Duplicate check)
    success, msg = db.mark_attendance(sid, name, subject, time_slot)
    print(f"Mark Attendance 2 (Should Fail): {success}, {msg}")
    
    if not success and "already marked" in msg:
        print("SUCCESS: Duplicate prevented.")
    else:
        print("FAILURE: Duplicate NOT prevented.")

    # 5. Verify Record
    record = db.attendance.find_one({"student_id": sid, "subject": subject})
    if record:
        print(f"SUCCESS: Attendance record found: {record.get('subject')} at {record.get('time')}")
        if record.get("time_slot") == time_slot:
             print("SUCCESS: Time slot recorded correctly.")
        else:
             print(f"FAILURE: Time slot mismatch. Expected {time_slot}, got {record.get('time_slot')}")
    else:
        print("FAILURE: Attendance record not found.")

    # 6. Cleanup
    db.timetables.delete_one({"subject": subject})
    db.attendance.delete_one({"student_id": sid})
    print("Cleanup done.")

except Exception as e:
    print(f"An error occurred: {e}")
