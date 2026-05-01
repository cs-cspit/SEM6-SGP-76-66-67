import customtkinter as ctk
import os
import sys

# Ensure parent path is available
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from database.db import db
from gui.mark_attendance import MarkAttendancePage

class AttendanceApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Smart Attendance - Capture Station")
        self.geometry("800x600")
        
        # Theme
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        # Container
        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True)
        
        # Shared DB reference (used by MarkAttendancePage)
        self.db = db
        
        # Load Attendance Page directly
        self.show_attendance()

    def show_attendance(self):
        page = MarkAttendancePage(self.container, self)
        page.pack(fill="both", expand=True)

if __name__ == "__main__":
    app = AttendanceApp()
    app.mainloop()
