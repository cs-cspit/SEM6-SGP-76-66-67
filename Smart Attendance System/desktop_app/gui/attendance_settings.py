import customtkinter as ctk
from tkinter import messagebox

class AttendanceSettingsPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Grid Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        
        # Title
        self.lbl_title = ctk.CTkLabel(self, text="Attendance Session Control", font=ctk.CTkFont(size=24, weight="bold"))
        self.lbl_title.grid(row=0, column=0, padx=20, pady=(40, 20), sticky="w")
        
        # --- Settings Frame ---
        self.settings_frame = ctk.CTkFrame(self)
        self.settings_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        # Duration
        self.lbl_duration = ctk.CTkLabel(self.settings_frame, text="Run Duration:", font=ctk.CTkFont(size=14))
        self.lbl_duration.grid(row=0, column=0, padx=20, pady=20, sticky="w")
        
        self.combo_duration = ctk.CTkComboBox(self.settings_frame, values=["3 Seconds", "1 Minute", "5 Minutes", "15 Minutes", "1 Hour", "Full Day"], width=200)
        self.combo_duration.grid(row=0, column=1, padx=20, pady=20, sticky="w")

        # Interval
        self.lbl_interval = ctk.CTkLabel(self.settings_frame, text="Repeat Interval:", font=ctk.CTkFont(size=14))
        self.lbl_interval.grid(row=1, column=0, padx=20, pady=20, sticky="w")
        
        self.combo_interval = ctk.CTkComboBox(self.settings_frame, values=["No Repeat", "5 Minutes", "15 Minutes", "30 Minutes", "1 Hour", "2 Hours"], width=200)
        self.combo_interval.grid(row=1, column=1, padx=20, pady=20, sticky="w")
        
        # Tip
        self.lbl_tip = ctk.CTkLabel(self.settings_frame, text="Note: Marks attendance for the specified duration, then waits for the interval.", text_color="gray")
        self.lbl_tip.grid(row=2, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="w")
        
        # --- Control Frame ---
        self.control_frame = ctk.CTkFrame(self)
        self.control_frame.grid(row=2, column=0, padx=20, pady=20, sticky="ew")
        
        self.status_label = ctk.CTkLabel(self.control_frame, text="System Status: UNKNOWN", font=ctk.CTkFont(size=18, weight="bold"))
        self.status_label.pack(side="top", pady=20)
        
        self.btn_start = ctk.CTkButton(self.control_frame, text="START ATTENDANCE SYSTEM", command=self.start_system, 
                                       fg_color="#2CC985", hover_color="#2EA06D", height=50, font=ctk.CTkFont(size=16, weight="bold"))
        self.btn_start.pack(side="left", padx=20, pady=20, expand=True, fill="x")
        
        self.btn_stop = ctk.CTkButton(self.control_frame, text="STOP SYSTEM", command=self.stop_system, 
                                      fg_color="#FF4C4C", hover_color="#C43B3B", height=50, font=ctk.CTkFont(size=16, weight="bold"))
        self.btn_stop.pack(side="left", padx=20, pady=20, expand=True, fill="x")
        
        # --- Email Settings Frame ---
        self.email_frame = ctk.CTkFrame(self)
        self.email_frame.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="ew")
        
        ctk.CTkLabel(self.email_frame, text="Automatic Email Configuration", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, columnspan=2, padx=20, pady=10, sticky="w")
        
        ctk.CTkLabel(self.email_frame, text="Sender Email:", font=ctk.CTkFont(size=14)).grid(row=1, column=0, padx=20, pady=10, sticky="w")
        self.entry_email = ctk.CTkEntry(self.email_frame, width=300, placeholder_text="e.g. system@gmail.com")
        self.entry_email.grid(row=1, column=1, padx=20, pady=10, sticky="w")
        
        ctk.CTkLabel(self.email_frame, text="App Password:", font=ctk.CTkFont(size=14)).grid(row=2, column=0, padx=20, pady=10, sticky="w")
        self.entry_password = ctk.CTkEntry(self.email_frame, width=300, show="*", placeholder_text="16-character App Password")
        self.entry_password.grid(row=2, column=1, padx=20, pady=10, sticky="w")
        
        self.btn_save_email = ctk.CTkButton(self.email_frame, text="Save Email Config", command=self.save_email_config, width=150)
        self.btn_save_email.grid(row=3, column=0, columnspan=2, padx=20, pady=20)
        
        # Initialize
        self.load_settings()

    def save_email_config(self):
        email = self.entry_email.get().strip()
        pwd = self.entry_password.get().strip()
        self.controller.db.set_email_config(email, pwd)
        messagebox.showinfo("Success", "Email configuration saved successfully!")

    def load_settings(self):
        config = self.controller.db.get_config()
        
        self.combo_duration.set(config.get('duration_str', 'Full Day'))
        self.combo_interval.set(config.get('interval_str', 'No Repeat'))
        
        is_active = config.get('is_active', False)
        self.update_status_ui(is_active)
        
        email_cfg = self.controller.db.get_email_config()
        self.entry_email.delete(0, 'end')
        self.entry_email.insert(0, email_cfg.get("sender_email", ""))
        self.entry_password.delete(0, 'end')
        self.entry_password.insert(0, email_cfg.get("app_password", ""))

    def update_status_ui(self, is_active):
        if is_active:
            self.status_label.configure(text="System Status: ACTIVE (RUNNING)", text_color="#2CC985")
            self.combo_duration.configure(state="disabled")
            self.combo_interval.configure(state="disabled")
            self.btn_start.configure(state="disabled")
            self.btn_stop.configure(state="normal")
        else:
            self.status_label.configure(text="System Status: INACTIVE (STOPPED)", text_color="#FF4C4C")
            self.combo_duration.configure(state="normal")
            self.combo_interval.configure(state="normal")
            self.btn_start.configure(state="normal")
            self.btn_stop.configure(state="disabled")

    def parse_time_str(self, time_str):
        """Converts string '5 Minutes' to seconds (int)."""
        time_str = time_str.lower()
        if "second" in time_str:
            return int(time_str.split()[0])
        elif "minute" in time_str:
            return int(time_str.split()[0]) * 60
        elif "hour" in time_str:
            return int(time_str.split()[0]) * 3600
        elif "day" in time_str:
            return 86400  # 24 hours
        return 0

    def start_system(self):
        dur_str = self.combo_duration.get()
        int_str = self.combo_interval.get()
        
        duration = self.parse_time_str(dur_str)
        interval = self.parse_time_str(int_str)
        
        self.controller.db.set_config(duration, interval, True, dur_str, int_str)
        self.update_status_ui(True)

    def stop_system(self):
        # We fetch current to preserve strings, or just update active status
        # Better to just update status
        self.controller.db.db.config.update_one(
             {"_id": "attendance_settings"},
             {"$set": {"is_active": False}}
        )
        self.update_status_ui(False)
