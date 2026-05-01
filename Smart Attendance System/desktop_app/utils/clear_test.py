import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.db import db

def clear_today():
    print("Clearing today's attendance to allow testing...")
    res = db.attendance.delete_many({"date": "2026-03-05"})
    print(f"Deleted {res.deleted_count} records from today.")

if __name__ == "__main__":
    clear_today()
