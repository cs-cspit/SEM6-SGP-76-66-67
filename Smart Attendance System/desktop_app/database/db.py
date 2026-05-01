import pymongo
from bcrypt import hashpw, checkpw, gensalt
from datetime import datetime

# --- Configuration ---
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "smart_attendance_db"

class Database:
    def __init__(self):
        try:
            self.client = pymongo.MongoClient(MONGO_URI)
            self.db = self.client[DB_NAME]
            self.students = self.db["students"]
            self.admins = self.db["admins"]
            self.attendance = self.db["attendance"]
            self.timetables = self.db["timetables"]
            print("Database connected successfully.")
            self._init_admin()
        except Exception as e:
            print(f"Database connection error: {e}")

    def _init_admin(self):
        """Creates a default admin if none exists."""
        if self.admins.count_documents({}) == 0:
            hashed_pw = hashpw("admin123".encode('utf-8'), gensalt())
            self.admins.insert_one({"username": "admin", "password": hashed_pw})
            print("Default admin created: admin / admin123")

    def verify_admin(self, username, password):
        admin = self.admins.find_one({"username": username})
        if admin:
            if checkpw(password.encode('utf-8'), admin['password']):
                return True
        return False

    def get_all_students(self):
        return list(self.students.find({}, {'_id': 0}))
    
    def get_student_by_id(self, student_id):
        return self.students.find_one({"student_id": student_id}, {'_id': 0})

    # --- Timetable Management ---
    def add_timetable_entry(self, day, start_time, end_time, subject, faculty="", section=""):
        """Adds a new class schedule."""
        entry = {
            "day": day,
            "start_time": start_time,
            "end_time": end_time,
            "subject": subject,
            "faculty": faculty,
            "section": section,
            "created_at": datetime.now()
        }
        self.timetables.insert_one(entry)
        return True, "Schedule added successfully"

    def get_timetables(self, day=None):
        query = {}
        if day:
            query["day"] = day
        # Sort by day and start time. Note: sorting by string time works if format is HH:MM (24h)
        return list(self.timetables.find(query).sort([("day", 1), ("start_time", 1)]))

    def delete_timetable_entry(self, entry_id):
        from bson.objectid import ObjectId
        try:
            self.timetables.delete_one({"_id": ObjectId(entry_id)})
            return True, "Deleted successfully"
        except Exception as e:
            return False, str(e)



    def mark_attendance(self, student_id, name, subject=None, time_slot=None):
        """Marks attendance. If subject provided, ensures unique entry for that subject/slot.
        If subject is None, marks as 'No Active Class'."""
        today = datetime.now().strftime("%Y-%m-%d")
        
        # If no subject provided, mark as "No Active Class"
        if subject is None:
            subject = "No Active Class"
            time_slot = "N/A"
        
        query = {
            "student_id": student_id,
            "date": today,
            "subject": subject
        }
        
        if time_slot:
            query["time_slot"] = time_slot
        
        existing = self.attendance.find_one(query)
        
        if existing:
            return False, f"Attendance already marked for {subject}"
        
        now = datetime.now()
        record = {
            "student_id": student_id,
            "name": name,
            "date": today,
            "time": now.strftime("%I:%M:%S %p"),
            "status": "Present",
            "subject": subject if subject else "General",
            "time_slot": time_slot if time_slot else ""
        }
        self.attendance.insert_one(record)
        
        # Trigger 'Present' Email
        from utils.email_sender import EmailSender
        student_data = self.get_student_by_id(student_id)
        if student_data and student_data.get('email'):
            EmailSender.send_present_notification(
                student_data['email'], 
                name, 
                subject if subject else "General", 
                time_slot if time_slot else "N/A", 
                today, 
                now.strftime("%I:%M:%S %p")
            )
            
        return True, f"Marked Present: {subject}" if subject else "Marked Present"

    def get_attendance_reports(self, date_filter=None):
        query = {}
        if date_filter:
            query["date"] = date_filter
        return list(self.attendance.find(query, {'_id': 0}).sort("date", -1))

    # --- Encodings Management ---
    def update_student_encodings(self, student_id, encodings):
        """
        Updates encodings for a specific student.
        :param encodings: List of numpy arrays
        """
        import pickle
        # Convert numpy arrays to binary
        binary_encodings = [pickle.dumps(enc) for enc in encodings]
        
        self.students.update_one(
            {"student_id": student_id},
            {"$set": {"encodings": binary_encodings}},
            upsert=True # Create if doesn't exist (though registration should handle it)
        )

    def get_all_encodings(self):
        """
        Returns a dict: { student_id: [numpy_array, ...] }
        """
        import pickle
        data = {}
        # Fetch only students who have encodings
        print(f"DEBUG: Querying students with encodings from {self.students.name}...")
        cursor = self.students.find({"encodings": {"$exists": True}}, {"student_id": 1, "encodings": 1, "_id": 0})
        
        count = 0
        for doc in cursor:
            count += 1
            sid = doc["student_id"]
            if "encodings" in doc:
                try:
                    # Deserialize back to numpy
                    encs = [pickle.loads(b) for b in doc["encodings"]]
                    data[sid] = encs
                except Exception as e:
                    print(f"Error decoding data for {sid}: {e}")
        print(f"DEBUG: Found {count} students with encodings in DB. Returning data.")
        return data

    # --- System Configuration ---
    def get_config(self):
        """Returns the current system configuration or defaults."""
        conf = self.db.config.find_one({"_id": "attendance_settings"})
        if not conf:
            return {
                "duration": 86400, # Full Day default
                "interval": 0,     # No repeat
                "is_active": False,
                "duration_str": "Full Day",
                "interval_str": "No Repeat"
            }
        return conf

    def set_config(self, duration, interval, is_active, duration_str, interval_str):
        """Updates the system configuration."""
        self.db.config.update_one(
            {"_id": "attendance_settings"},
            {"$set": {
                "duration": duration,
                "interval": interval,
                "is_active": is_active,
                "duration_str": duration_str,
                "interval_str": interval_str
            }},
            upsert=True
        )

    def set_manual_session(self, timetable_id):
        """Sets a manual override for the active class and activates system."""
        from bson.objectid import ObjectId
        self.db.config.update_one(
            {"_id": "attendance_settings"},
            {"$set": {
                "manual_session_id": str(timetable_id),
                "is_active": True
            }},
            upsert=True
        )

    def clear_manual_session(self):
        """Clears the manual session override and stops system."""
        self.db.config.update_one(
            {"_id": "attendance_settings"},
            {"$unset": {"manual_session_id": ""}, "$set": {"is_active": False}}
        )

    def get_active_class(self):
        """Returns the current active class based on Time."""
        # 1. Manual Override (Disabled by request)
        # conf = self.get_config()
        # manual_id = conf.get("manual_session_id")
        # if manual_id: ...

        # 2. Time Based (Default)
        now = datetime.now()
        day_name = now.strftime("%A") 
        current_time_str = now.strftime("%H:%M") 
        
        query = {
            "day": day_name,
            "start_time": {"$lte": current_time_str},
            "end_time": {"$gte": current_time_str}
        }
        
        return self.timetables.find_one(query)

    # --- Analytics & Email Config ---
    def get_email_config(self):
        conf = self.db.config.find_one({"_id": "email_settings"})
        if not conf:
            return {"sender_email": "", "app_password": ""}
        return conf

    def set_email_config(self, sender_email, app_password):
        self.db.config.update_one(
            {"_id": "email_settings"},
            {"$set": {"sender_email": sender_email, "app_password": app_password}},
            upsert=True
        )

    def get_absent_students(self, date_str, subject=None, time_slot=None):
        all_students = self.get_all_students()
        query = {"date": date_str}
        if subject and subject != "No Active Class":
            query["subject"] = subject
        if time_slot and time_slot != "N/A":
            query["time_slot"] = time_slot
            
        present_records = list(self.attendance.find(query, {"student_id": 1}))
        present_ids = {record["student_id"] for record in present_records}
        
        absent = []
        for s in all_students:
            if s["student_id"] not in present_ids:
                absent.append(s)
        return absent

    def get_attendance_stats_for_date(self, date_str):
        all_students_count = self.students.count_documents({})
        records = list(self.attendance.find({"date": date_str}, {"student_id": 1}))
        present_count = len({r["student_id"] for r in records})
        absent_count = max(0, all_students_count - present_count)
        return {"total": all_students_count, "present": present_count, "absent": absent_count}

    def get_monthly_trend(self, month_year):
        query = {"date": {"$regex": f"^{month_year}"}}
        records = list(self.attendance.find(query, {"date": 1, "student_id": 1}))
        trend = {}
        for r in records:
            d = r["date"]
            if d not in trend: trend[d] = set()
            trend[d].add(r["student_id"])
        
        # Count unique students present each day
        return {d: len(sids) for d, sids in trend.items()}

db = Database()
