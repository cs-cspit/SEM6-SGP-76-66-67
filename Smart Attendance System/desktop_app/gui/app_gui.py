import customtkinter as ctk
from PIL import Image
import os
import sys

# Add parent directory to path to find other modules if run from here
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from database.db import db

# Import Frames (Placeholder for now, will implement next)
# We will implement these in the same file or separate? Separate is cleaner.
# But for now, I'll structure the imports assuming they exist, then create them.
# To avoid ImportErrors while writing, I will implement the GUI logic in this file or defer imports.
# Given "file by file" requirement, I should probably implement the frames first or implement a shell here.
# Let's implement the shell and the frames in separate files for "Industry Grade" structure.

# Since I can't import what doesn't exist, I will create the frame files after this.
# But `app_gui.py` is the controller.

class SmartAttendanceApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Smart Attendance System - Admin Panel")
        self.geometry("1200x800")
        
        # Theme
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

        # Container for frames
        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True)
        
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        
        # Store shared resources
        self.db = db
        self.icons = {}
        self.load_assets()

    def load_assets(self):
        # Load Icons
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'assets', 'icons')
        
        try:
            self.icons['dashboard'] = ctk.CTkImage(light_image=Image.open(os.path.join(icon_path, 'dashboard.png')), dark_image=Image.open(os.path.join(icon_path, 'dashboard.png')), size=(20, 20))
            self.icons['student'] = ctk.CTkImage(light_image=Image.open(os.path.join(icon_path, 'student.png')), dark_image=Image.open(os.path.join(icon_path, 'student.png')), size=(20, 20))
            self.icons['train'] = ctk.CTkImage(light_image=Image.open(os.path.join(icon_path, 'train.png')), dark_image=Image.open(os.path.join(icon_path, 'train.png')), size=(20, 20))
            self.icons['reports'] = ctk.CTkImage(light_image=Image.open(os.path.join(icon_path, 'reports.png')), dark_image=Image.open(os.path.join(icon_path, 'reports.png')), size=(20, 20))
            self.icons['logout'] = ctk.CTkImage(light_image=Image.open(os.path.join(icon_path, 'logout.png')), dark_image=Image.open(os.path.join(icon_path, 'logout.png')), size=(20, 20))
        except Exception as e:
            print(f"Error loading icons: {e}")
            
        # We will initialize frames here after we define them.
        # For now, let's just setup the switching mechanism and a Login Page placeholder.
        # I'll modify this file later to import the actual classes if separate, 
        # or I can put EVERYTHING layout-related here if the user prefers "FULL CODE". 
        # But separating is better.
        
        # Let's use string-based lazy loading or just import at top?
        # I'll assume `from gui.login_page import LoginPage` works.
        # I will CREATE the frames now inside this tool call series to avoid import errors when running?
        # No, I can't write multiple files in one tool call (except wait, I can parallelize slightly or just write them sequentially).
        
        # Start with just showing Login.
        
        self.show_login()

    def show_login(self):
        # Clear container
        for widget in self.container.winfo_children():
            widget.destroy()
            
        from gui.login_page import LoginPage
        frame = LoginPage(parent=self.container, controller=self)
        frame.grid(row=0, column=0, sticky="nsew")
        
    def show_dashboard(self):
        try:
            # Clear container
            for widget in self.container.winfo_children():
                widget.destroy()
                
            from gui.dashboard import Dashboard
            frame = Dashboard(parent=self.container, controller=self)
            frame.grid(row=0, column=0, sticky="nsew")
        except Exception as e:
            import traceback
            error_msg = f"Error loading Dashboard:\n{str(e)}\n\n{traceback.format_exc()}"
            print(error_msg)
            from tkinter import messagebox
            messagebox.showerror("Dashboard Error", error_msg)

# Note: The imports inside methods are to avoid circular imports and ensure files exist when called (if created dynamically)
