import customtkinter as ctk
import cv2
from PIL import Image, ImageTk
import threading
import time
from datetime import datetime
import os
import csv
from utils.face_recognizer import FaceRecognizer
from utils.cnn_anti_spoofing import CNNAntiSpoofing
from utils.email_sender import EmailSender

class MarkAttendancePage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # --- UI Layout (Simplifed) ---
        # Camera Feed takes up most space
        self.camera_frame = ctk.CTkFrame(self)
        self.camera_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        self.video_label = ctk.CTkLabel(self.camera_frame, text="Waiting for Admin to Start System...", font=ctk.CTkFont(size=20))
        self.video_label.pack(expand=True, fill="both")
        
        # Status Bar at Bottom
        self.status_frame = ctk.CTkFrame(self, height=40)
        self.status_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))
        
        self.status_label = ctk.CTkLabel(self.status_frame, text="Status: IDLE", font=ctk.CTkFont(size=14, weight="bold"))
        self.status_label.pack(side="left", padx=20, pady=5)
        
        self.timer_label = ctk.CTkLabel(self.status_frame, text="", font=ctk.CTkFont(size=14), text_color="#FFD700")
        self.timer_label.pack(side="left", padx=20, pady=5)

        self.total_faces_label = ctk.CTkLabel(self.status_frame, text="Total: 0", font=ctk.CTkFont(size=14, weight="bold"), text_color="#FFFFFF")
        self.total_faces_label.pack(side="left", padx=10, pady=5)

        self.attendance_count_label = ctk.CTkLabel(self.status_frame, text="Present: 0", font=ctk.CTkFont(size=14, weight="bold"), text_color="#00FF00")
        self.attendance_count_label.pack(side="left", padx=10, pady=5)

        self.unknown_count_label = ctk.CTkLabel(self.status_frame, text="Unknown/Spoof: 0", font=ctk.CTkFont(size=14, weight="bold"), text_color="#FF4C4C")
        self.unknown_count_label.pack(side="left", padx=10, pady=5)        
        self.class_label = ctk.CTkLabel(self.status_frame, text="No Active Class", font=ctk.CTkFont(size=14), text_color="#FFA500")
        self.class_label.pack(side="right", padx=20, pady=5)

        # --- Variables ---
        self.cap = None
        self.is_running = True # App lifecycle
        self.is_camera_mining = False # Actual camera state
        
        self.recognizer = FaceRecognizer()
        self.anti_spoofing = CNNAntiSpoofing()
        self.spoof_logs_path = "spoof_logs.csv"
        self.spoof_cooldowns = {}
        
        # Attendance Logic Variables
        self.marked_today = set()
        self.face_trackers = {}
        self.last_results = []
        self.frame_count = 0
        self.process_interval = 4
        
        # Start Controller Thread
        self.thread = threading.Thread(target=self.main_loop, daemon=True)
        self.thread.start()

    def main_loop(self):
        """
        Main Loop:
        1. Poll DB for config.
        2. If Active:
           - Start Camera
           - Run for Duration (checking Active constantly)
           - Stop Camera
           - Wait Interval (checking Active constantly)
        3. If Inactive:
           - Ensure Camera Stopped
           - Wait 1s
        """
        while self.is_running:
            try:
                config = self.controller.db.get_config()
                is_active = config.get('is_active', False)
                
                if not is_active:
                    self.stop_camera()
                    self.update_status("System Stopped by Admin", "")
                    time.sleep(1)
                    continue
                
                # --- System IS Active ---
                duration = config.get('duration', 86400)
                interval = config.get('interval', 0)
                
                # 1. Start Scan Session
                self.start_camera()
                start_time = time.time()
                end_time = start_time + duration
                
                self.marked_today.clear() # Reset session cache
                
                # Run Pattern
                while self.is_running and time.time() < end_time:
                    # Check if Admin paused it mid-run
                    curr_config = self.controller.db.get_config()
                    if not curr_config.get('is_active', False):
                        break # Go back to outer loop to handle stop
                        
                    remaining = int(end_time - time.time())
                    self.update_status("Scanning...", f"Ends in: {remaining//60:02d}:{remaining%60:02d}")
                    
                    # Camera is updated by its own thread/logic? 
                    # Actually, we need to run camera processing.
                    # Since we are in a thread, we can just call a "tick" function or use a separate camera thread.
                    # Implementation detail: 'start_camera' spins up a camera thread inside?
                    # Yes, let's keep the camera reading in a separate thread/loop or just handle frame reading here?
                    # Merging them might be safer for resource management, but let's stick to existing pattern:
                    # start_camera creates 'self.camera_thread'.
                    
                    time.sleep(1)
                
                # 2. Stop Scan Session
                self.stop_camera()
                
                # Automatically Email Absentees (If a valid class was running)
                active_class = self.controller.db.get_active_class()
                if active_class:
                    subject = active_class['subject']
                    time_slot = f"{active_class['start_time']}-{active_class['end_time']}"
                    date_str = datetime.now().strftime("%Y-%m-%d")
                    absentees = self.controller.db.get_absent_students(date_str, subject, time_slot)
                    for a in absentees:
                        if a.get('email'):
                            EmailSender.send_absent_notification(a['email'], a.get('name', 'Student'), subject, time_slot, date_str)
                
                if not self.is_running: break
                
                # Check config again before waiting
                curr_config = self.controller.db.get_config()
                if not curr_config.get('is_active', False):
                    continue
                
                if interval == 0: # No Repeat
                    # If "Full Day" or "No Repeat", we might just stop or stay active?
                    # If "No Repeat", we finish and wait for admin to toggle off/on?
                    # We will mark we are done.
                    self.update_status("Session Completed", "Waiting for Admin")
                    while self.is_running:
                         if not self.controller.db.get_config().get('is_active', False):
                             break
                         time.sleep(1)
                    continue

                # 3. Wait Pattern (Interval)
                # Interval is usually "Time between starts" or "Time between end and start"?
                # Plan said: "Wait for [Interval - Duration]" (Start-to-Start) or just "Wait Interval"?
                # "Repeat Every 1 Hour" usually means Start-to-Start.
                # Let's assume Interval is "Rest Time" for simplicity if Plan was ambiguous?
                # Actually Config names are "5 Minutes", "1 Hour".
                # If Run=5m, Repeat=1h. It implies 5m ON, 55m OFF.
                
                elapsed = time.time() - start_time
                wait_time = interval - elapsed
                if wait_time < 0: wait_time = 0
                
                wait_end = time.time() + wait_time
                
                while self.is_running and time.time() < wait_end:
                     # Check if Admin paused
                    if not self.controller.db.get_config().get('is_active', False):
                        break

                    remaining = int(wait_end - time.time())
                    self.update_status("Waiting next session...", f"Starts in: {remaining//60:02d}:{remaining%60:02d}")
                    time.sleep(1)
                    
            except Exception as e:
                print(f"Error in main loop: {e}")
                time.sleep(1)

    def update_status(self, status, timer):
        # Schedule UI update on main thread
        self.status_label.configure(text=f"Status: {status}")
        self.timer_label.configure(text=timer)

    def start_camera(self):
        if self.is_camera_mining: return
        
        # Reload model
        if not self.recognizer.load_model():
             self.update_status("Error: Model Missing", "")
             return
             
        self.is_camera_mining = True
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        # Reset trackers
        self.face_trackers.clear() 
        self.last_results = []
        
        self.last_frame = None
        self.camera_thread = threading.Thread(target=self.video_loop, daemon=True)
        self.camera_thread.start()
        self.update_gui()

    def stop_camera(self):
        self.is_camera_mining = False
        if hasattr(self, 'camera_thread') and self.camera_thread and self.camera_thread.is_alive():
            self.camera_thread.join(timeout=1.0)
            
        if self.cap:
            self.cap.release()
            self.cap = None
        
        # UI Reset
        try:
            self.video_label.configure(image=None, text="Waiting for Admin/Interval...")
        except: pass

    def video_loop(self):
        while self.is_camera_mining and self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret: break
            
            self.frame_count += 1
            if self.frame_count % self.process_interval == 0:
                self.process_frame_logic(frame)
            
            self.draw_results(frame)
            
            # Convert for Tkinter here to save main thread work? 
            # Or just store raw frame? 
            # Let's store raw frame (BGR) to avoid race conditions with image objects
            # Actually, let's do color conversion here so main thread just re-wraps it.
            try:
                # Resize for display performance
                display_w, display_h = 640, 480
                frame_resized = cv2.resize(frame, (display_w, display_h))
                frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
                self.last_frame = Image.fromarray(frame_rgb)
            except Exception as e:
                print(f"Frame error: {e}")
                continue
            
            # Small sleep to yield
            time.sleep(0.01)
            
        if self.cap: self.cap.release()

    def update_gui(self):
        if not self.is_camera_mining:
            return

        # Update Count - Count only unique student IDs (not the full keys with subject)
        unique_students = set()
        for key in self.marked_today:
            # Extract student_id from keys like "23cs076_Math" or "23cs082_no_class"
            student_id = key.split('_')[0]
            unique_students.add(student_id)
        
        count = len(unique_students)
        self.attendance_count_label.configure(text=f"Present: {count}")

        # Update Live Counters
        total_faces = len(self.last_results)
        unknown_faces = sum(1 for res in self.last_results if not res['id'] or res['id'] == "")
        spoof_faces = sum(1 for res in self.last_results if "SPOOF" in res['status'] or "Low Conf" in res['status'])
        
        self.total_faces_label.configure(text=f"Total: {total_faces}")
        self.unknown_count_label.configure(text=f"Fail/Spoof: {unknown_faces + spoof_faces}")

        if self.last_frame:
            try:
                ctk_img = ctk.CTkImage(light_image=self.last_frame, dark_image=self.last_frame, size=(640, 480))
                self.video_label.configure(image=ctk_img, text="")
                
            except Exception as e:
                print(f"UI Update Error: {e}")
        
        # Schedule next update
        if self.is_running and self.is_camera_mining:
            self.after(30, self.update_gui)

    def process_frame_logic(self, frame):
        # (Same logic as before, just copying essential parts)
        active_class = self.controller.db.get_active_class()
        if active_class:
            subject = active_class['subject']
            time_slot = f"{active_class['start_time']}-{active_class['end_time']}"
            
            # Check for manual flag
            if active_class.get('is_manual'):
                txt = f"MANUAL: {subject} ({time_slot})"
                color = "#E0A800" # Amber/Gold
            else:
                txt = f"Class: {subject} ({time_slot})"
                color = "#2CC985" # Green
                
            try: self.class_label.configure(text=txt, text_color=color)
            except: pass
        else:
            # No active class - still mark attendance but with special status
            try: self.class_label.configure(text="No Active Class", text_color="#FFA500")
            except: pass
            subject = "No Active Class"
            time_slot = "N/A"

        raw_results = self.recognizer.recognize_frame(frame)
        current_ids = set()
        new_results = []
        
        for res in raw_results:
            student_id = res['id']
            conf = res['conf']
            box = res['box']
            name = "Unknown"
            status_text = "Scanning..."
            color = (0, 0, 255)
            
            if student_id:
                current_ids.add(student_id)
                student_data = self.controller.db.get_student_by_id(student_id)
                name = student_data.get('name', 'Unregistered') if student_data else "Unregistered"
                
                if name != "Unregistered":
                    now = time.time()
                    if student_id not in self.face_trackers:
                        self.face_trackers[student_id] = {
                            'first_seen': now, 
                            'last_seen': now, 
                            'consecutive_frames': 0
                        }
                    
                    tracker = self.face_trackers[student_id]
                    tracker['last_seen'] = now
                    tracker['consecutive_frames'] += 1
                    
                    duration = now - tracker['first_seen']
                    is_valid = conf >= 60
                    
                    # CNN Anti-Spoofing
                    spoof_res = self.anti_spoofing.predict(frame, box)
                    is_real = spoof_res['label'] == 'REAL' and spoof_res['confidence'] > 0.85
                    
                    # Cooldown logic
                    in_cooldown = now - self.spoof_cooldowns.get(student_id, 0) < 3.0
                    
                    if not is_real:
                        self._log_spoof_attempt(student_id, spoof_res['confidence'])
                        self.spoof_cooldowns[student_id] = now
                        status_text = "SPOOF ATTEMPT BLOCKED"
                        color = (0, 0, 255)
                    elif in_cooldown:
                        status_text = "SPOOF ATTEMPT BLOCKED"
                        color = (0, 0, 255)
                    else:
                        key = f"{student_id}_{subject}" if subject != "No Active Class" else f"{student_id}_no_class"
                        
                        if key in self.marked_today:
                            status_text = f"PRESENT: {subject}" if subject != "No Active Class" else "PRESENT (No Class)"
                            color = (0, 255, 0) if subject != "No Active Class" else (255, 165, 0)
                        elif is_valid and is_real:
                            success, _ = self.controller.db.mark_attendance(student_id, name, subject, time_slot)
                            if success:
                                self.marked_today.add(key)
                                status_text = f"PRESENT: {subject}" if subject != "No Active Class" else "PRESENT (No Class)"
                                color = (0, 255, 0) if subject != "No Active Class" else (255, 165, 0)
                            else:
                                status_text = f"PRESENT: {subject}" if subject != "No Active Class" else "PRESENT (No Class)"
                                color = (0, 255, 0) if subject != "No Active Class" else (255, 165, 0)
                        elif is_valid:
                            status_text = "LIVE FACE DETECTED"
                            color = (0, 255, 255)
                        else:
                            status_text = f"Low Conf {conf:.0f}%"
                            color = (0, 165, 255)
            
            new_results.append({'box': box, 'name': name, 'id': student_id, 'status': status_text, 'color': color})

        for sid in list(self.face_trackers.keys()):
            if sid not in current_ids:
                del self.face_trackers[sid]
        
        self.last_results = new_results

    def _log_spoof_attempt(self, student_id, confidence):
        try:
            file_exists = os.path.isfile(self.spoof_logs_path)
            with open(self.spoof_logs_path, mode='a', newline='') as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(["Timestamp", "Student ID", "Spoof Confidence"])
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                writer.writerow([timestamp, student_id, f"{confidence:.2f}"])
        except Exception as e:
            print(f"Error logging spoof attempt: {e}")

    def draw_results(self, frame):
        for res in self.last_results:
            x, y, w, h = res['box']
            
            # Draw Bounding Box
            cv2.rectangle(frame, (x, y), (x+w, y+h), res['color'], 3) # Thicker box (2->3)
            
            # Draw Background for Text (Expanded for larger text)
            # Was y-40, increasing to y-70 to fit 2 lines of larger text
            cv2.rectangle(frame, (x, y-70), (x+w, y), res['color'], -1)
            
            # Student Name & ID
            label = f"{res['name']} ({res['id']})" if res['id'] else res['name']
            # Increased font: 0.5 -> 0.8, Thickness: 1 -> 2
            cv2.putText(frame, label, (x+5, y-40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            
            # Status (PRESENT, Scanning...)
            # Increased font: 0.6 -> 0.9, Thickness: 2 -> 2 (Already bold)
            cv2.putText(frame, res['status'], (x+5, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)



    def destroy(self):
        self.is_running = False
        self.stop_camera()
        super().destroy()
