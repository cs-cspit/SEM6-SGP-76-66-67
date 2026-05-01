import os
import sys

# Setup Path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.db import db
from datetime import datetime

def test_queries():
    print("Testing DB Analytics Queries...")
    
    today = datetime.now().strftime("%Y-%m-%d")
    month = datetime.now().strftime("%Y-%m")
    
    # Test Absent Query
    try:
        absent = db.get_absent_students(today, "TestSubject", "10:00-11:00")
        print(f"[OK] Absent query successful. Found {len(absent)} absent students.")
    except Exception as e:
        print(f"[FAIL] Absent query error: {e}")

    # Test Stats Query
    try:
        stats = db.get_attendance_stats_for_date(today)
        print(f"[OK] Stats query successful: {stats}")
    except Exception as e:
        print(f"[FAIL] Stats query error: {e}")

    # Test Monthly Trend
    try:
        trend = db.get_monthly_trend(month)
        print(f"[OK] Monthly trend successful: {trend}")
    except Exception as e:
        print(f"[FAIL] Monthly trend error: {e}")

    # Test Email Config
    try:
        cfg = db.get_email_config()
        print(f"[OK] Email config fetch successful. Has email: {bool(cfg.get('sender_email'))}")
    except Exception as e:
        print(f"[FAIL] Email config error: {e}")


if __name__ == "__main__":
    test_queries()
