import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from datetime import datetime

class AnalyticsPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure((1, 2), weight=1)
        
        # Header
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        ctk.CTkLabel(self.header_frame, text="Attendance Analytics & Insights", font=ctk.CTkFont(size=24, weight="bold")).pack(side="left", padx=20)
        
        self.btn_refresh = ctk.CTkButton(self.header_frame, text="Refresh Data", command=self.load_charts, width=120)
        self.btn_refresh.pack(side="right", padx=20)

        # Content Area - Scrollable or just grids
        self.content_frame = ctk.CTkScrollableFrame(self)
        self.content_frame.grid(row=1, column=0, columnspan=2, rowspan=2, sticky="nsew", padx=10, pady=10)
        self.content_frame.grid_columnconfigure((0, 1), weight=1)

        # Chart Containers
        self.frame_pie = ctk.CTkFrame(self.content_frame)
        self.frame_pie.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        ctk.CTkLabel(self.frame_pie, text="Today's Overview (Present vs Absent)", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)
        self.canvas_pie = None

        self.frame_bar = ctk.CTkFrame(self.content_frame)
        self.frame_bar.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        ctk.CTkLabel(self.frame_bar, text="Daily Trend (Bar Chart - This Month)", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)
        self.canvas_bar = None

        self.frame_line = ctk.CTkFrame(self.content_frame)
        self.frame_line.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        ctk.CTkLabel(self.frame_line, text="Monthly Trend (Line Chart)", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)
        self.canvas_line = None

        self.load_charts()

    def load_charts(self):
        # Clear previous charts explicitly
        if self.canvas_pie: self.canvas_pie.get_tk_widget().destroy()
        if self.canvas_bar: self.canvas_bar.get_tk_widget().destroy()
        if self.canvas_line: self.canvas_line.get_tk_widget().destroy()
        
        today_str = datetime.now().strftime("%Y-%m-%d")
        month_str = datetime.now().strftime("%Y-%m")
        
        # 1. PIE CHART
        stats = self.controller.db.get_attendance_stats_for_date(today_str)
        fig_pie = Figure(figsize=(4, 3), facecolor='#2b2b2b')
        ax_pie = fig_pie.add_subplot(111)
        
        if stats['total'] > 0:
            labels = ['Present', 'Absent']
            sizes = [stats['present'], stats['absent']]
            colors = ['#2CC985', '#FF4C4C']
            # Only plot if sum > 0
            if sum(sizes) > 0:
                ax_pie.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140, textprops={'color':"w"})
            else:
                ax_pie.text(0.5, 0.5, '0 Students', color='white', ha='center', va='center')
                ax_pie.axis('off')
        else:
            ax_pie.text(0.5, 0.5, 'No Students Registered', color='white', ha='center', va='center')
            ax_pie.axis('off')
            
        self.canvas_pie = FigureCanvasTkAgg(fig_pie, master=self.frame_pie)
        self.canvas_pie.draw()
        self.canvas_pie.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)
        
        # 2. BAR CHART & LINE CHART (Monthly Trend)
        trend_data = self.controller.db.get_monthly_trend(month_str)
        
        fig_bar = Figure(figsize=(5, 3), facecolor='#2b2b2b')
        ax_bar = fig_bar.add_subplot(111)
        ax_bar.set_facecolor('#2b2b2b')
        ax_bar.tick_params(colors='white')
        [spine.set_color('white') for spine in ax_bar.spines.values()]
        
        fig_line = Figure(figsize=(8, 3), facecolor='#2b2b2b')
        ax_line = fig_line.add_subplot(111)
        ax_line.set_facecolor('#2b2b2b')
        ax_line.tick_params(colors='white')
        [spine.set_color('white') for spine in ax_line.spines.values()]

        if trend_data:
            days = sorted(list(trend_data.keys()))
            counts = [trend_data[d] for d in days]
            day_labels = [d.split('-')[2] for d in days] # Extract just day MM-DD -> DD
            
            # Bar 
            ax_bar.bar(day_labels, counts, color='#3B8ED0')
            ax_bar.set_ylabel('Students', color='white')
            ax_bar.set_xlabel('Day', color='white')

            # Line
            ax_line.plot(day_labels, counts, marker='o', color='#E0A800', linewidth=2)
            ax_line.set_ylabel('Students Present', color='white')
            ax_line.set_xlabel('Day of Month', color='white')
            ax_line.grid(True, linestyle='--', alpha=0.3, color='white')
            ax_line.set_ylim(bottom=0)
            
        else:
            for ax in (ax_bar, ax_line):
                ax.text(0.5, 0.5, 'No Attendance Data for This Month', color='white', ha='center', va='center')
                ax.axis('off')

        fig_bar.tight_layout()
        self.canvas_bar = FigureCanvasTkAgg(fig_bar, master=self.frame_bar)
        self.canvas_bar.draw()
        self.canvas_bar.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)

        fig_line.tight_layout()
        self.canvas_line = FigureCanvasTkAgg(fig_line, master=self.frame_line)
        self.canvas_line.draw()
        self.canvas_line.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)
