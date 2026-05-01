import customtkinter as ctk
from gui.student_view import StudentView
from gui.train_page import TrainPage
from gui.attendance_settings import AttendanceSettingsPage
from gui.reports_page import ReportsPage
from gui.analytics_page import AnalyticsPage
from gui.timetable_page import TimetablePage
from PIL import Image
import os

class Dashboard(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Main Layout: Sidebar (Left) + Content (Right)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # --- Sidebar ---
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0, fg_color="#212121") # Darker sidebar
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(7, weight=1) # Spacer push logout down
        
        # Logo / Title
        self.logo_label = ctk.CTkLabel(self.sidebar, text="  Smart Attendance", 
                                      font=ctk.CTkFont(family="Roboto", size=22, weight="bold"),
                                      image=self.controller.icons.get('dashboard', None),
                                      compound="left")
        self.logo_label.grid(row=0, column=0, padx=20, pady=(40, 30), sticky="w")
        
        # Sidebar Buttons
        self.btn_students = self.create_sidebar_button("Students", "student", self.show_students, 1)
        self.btn_train = self.create_sidebar_button("Train Model", "train", self.show_train, 2)
        self.btn_timetable = self.create_sidebar_button("Timetable", "reports", self.show_timetable, 3)
        self.btn_reports = self.create_sidebar_button("Reports", "reports", self.show_reports, 4)
        self.btn_analytics = self.create_sidebar_button("Analytics", "dashboard", self.show_analytics, 5) 
        self.btn_settings = self.create_sidebar_button("Attendance Control", "reports", self.show_settings, 6) # Recycle icon for now
        
        # Logout
        self.btn_logout = ctk.CTkButton(self.sidebar, text="  Logout", 
                                        command=self.logout,
                                        image=self.controller.icons.get('logout', None),
                                        compound="left",
                                        anchor="w",
                                        fg_color="transparent", 
                                        text_color="#e74c3c", 
                                        hover_color="#2c3e50",
                                        height=40,
                                        font=ctk.CTkFont(size=14, weight="bold"))
        self.btn_logout.grid(row=8, column=0, padx=20, pady=30, sticky="ew")
        
        # --- Content Area ---
        self.content_area = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.content_area.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.content_area.grid_columnconfigure(0, weight=1)
        self.content_area.grid_rowconfigure(0, weight=1)
        
        # State
        self.current_frame = None
        self.buttons = [self.btn_students, self.btn_train, self.btn_timetable, self.btn_reports, self.btn_analytics, self.btn_settings]
        
        self.show_students() # Default
        
    def create_sidebar_button(self, text, icon_key, command, row):
        btn = ctk.CTkButton(self.sidebar, text=f"  {text}", 
                            command=command,
                            image=self.controller.icons.get(icon_key, None),
                            compound="left",
                            anchor="w",
                            height=45,
                            font=ctk.CTkFont(size=15, weight="bold"),
                            fg_color="transparent",
                            text_color="white",
                            hover_color="#3B8ED0",
                            corner_radius=10)
        btn.grid(row=row, column=0, padx=15, pady=8, sticky="ew")
        return btn

    def set_active_button(self, active_btn):
        for btn in self.buttons:
            btn.configure(fg_color="transparent", text_color="white") # Reset
            
        active_btn.configure(fg_color="#3B8ED0", text_color="white")

    def show_students(self):
        self.switch_frame(StudentView, "students")
        self.set_active_button(self.btn_students)
        
    def show_train(self):
        self.switch_frame(TrainPage, "train")
        self.set_active_button(self.btn_train)

    def show_timetable(self):
        self.switch_frame(TimetablePage, "timetable")
        self.set_active_button(self.btn_timetable)
        
    def show_reports(self):
        self.switch_frame(ReportsPage, "reports")
        self.set_active_button(self.btn_reports)

    def show_analytics(self):
        self.switch_frame(AnalyticsPage, "analytics")
        self.set_active_button(self.btn_analytics)

    def show_settings(self):
        self.switch_frame(AttendanceSettingsPage, "settings")
        self.set_active_button(self.btn_settings)

    def switch_frame(self, frame_class, name):
        if self.current_frame:
            self.current_frame.destroy()
            
        self.current_frame = frame_class(self.content_area, self.controller)
        self.current_frame.grid(row=0, column=0, sticky="nsew")

    def logout(self):
        self.controller.show_login()
