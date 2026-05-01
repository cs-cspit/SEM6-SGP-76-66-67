import customtkinter as ctk
from tkinter import ttk
import pandas as pd
from tkinter import filedialog, messagebox
from tkcalendar import DateEntry
from datetime import datetime

class ReportsPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Grid Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header / Control Bar
        self.control_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.control_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        ctk.CTkLabel(self.control_frame, text="Attendance Reports", font=ctk.CTkFont(size=24, weight="bold")).pack(side="left")
        
        # Export Buttons (Right Side)
        self.btn_export_csv = ctk.CTkButton(self.control_frame, text="Export CSV", command=self.export_csv, width=100, fg_color="#3B8ED0")
        self.btn_export_csv.pack(side="right", padx=5)
        
        self.btn_export_excel = ctk.CTkButton(self.control_frame, text="Export Excel", command=self.export_excel, width=100, fg_color="#2CC985", hover_color="#219a64")
        self.btn_export_excel.pack(side="right", padx=5)
        
        # Filter Area (Left Side, next to title)
        self.filter_frame = ctk.CTkFrame(self.control_frame, fg_color="#2b2b2b", corner_radius=10) # Darker background
        self.filter_frame.pack(side="left", padx=20)
        
        ctk.CTkLabel(self.filter_frame, text="Date:", font=("Roboto", 12)).pack(side="left", padx=10)
        
        # DateEntry Theme Trick
        self.date_entry = DateEntry(self.filter_frame, width=12, background='#3B8ED0',
                                    foreground='white', borderwidth=0, date_pattern='yyyy-mm-dd')
        self.date_entry.pack(side="left", padx=5, pady=5)
        
        self.btn_filter = ctk.CTkButton(self.filter_frame, text="Filter", width=60, height=25, command=self.filter_data)
        self.btn_filter.pack(side="left", padx=10, pady=5)
        
        # Attendance Status Filter
        self.combo_status = ctk.CTkComboBox(self.filter_frame, values=["Present", "Absent"], width=100)
        self.combo_status.pack(side="left", padx=5, pady=5)
        self.combo_status.set("Present")

        self.refresh_btn = ctk.CTkButton(self.filter_frame, text="Show All", width=70, height=25, fg_color="transparent", border_width=1, command=self.load_data)
        self.refresh_btn.pack(side="left", padx=5, pady=5)

        # ---------------- Table Area ----------------
        self.tree_frame = ctk.CTkFrame(self)
        self.tree_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 0)) # Full width
        
        # Style Treeview (Shared style ideally, but re-declaring ensures it works regardless of init order)
        style = ttk.Style()
        style.theme_use("clam")
        
        bg_color = "#2b2b2b"
        text_color = "white"
        selected_color = "#3B8ED0"
        
        style.configure("Treeview", 
                        background=bg_color, 
                        foreground=text_color, 
                        fieldbackground=bg_color, 
                        rowheight=30,
                        font=("Roboto", 11),
                        borderwidth=0)
        style.configure("Treeview.Heading", background="#212121", foreground="white", relief="flat", font=("Roboto", 12, "bold"))
        style.map('Treeview', background=[('selected', selected_color)])
        
        columns = ("Student ID", "Name", "Date", "Time", "Subject", "Time Slot", "Status")
        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings")
        
        self.vsb = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.vsb.set)
        self.vsb.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)
        
        for col in columns:
            self.tree.heading(col, text=col)
            # Adjust widths
            if col in ["Subject", "Time Slot"]:
                self.tree.column(col, width=120, anchor="center")
            else:
                self.tree.column(col, width=100, anchor="center")
            
        self.load_data()

    def filter_data(self):
        selected_date = self.date_entry.get_date()
        date_str = selected_date.strftime("%Y-%m-%d")
        status_filter = self.combo_status.get()
        self.load_data(date_filter=date_str, status_filter=status_filter)

    def load_data(self, date_filter=None, status_filter="Present"):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        if status_filter == "Absent" and date_filter:
            data = self.controller.db.get_absent_students(date_filter)
            for row in data:
                self.tree.insert("", "end", values=(
                    row.get("student_id"),
                    row.get("name"),
                    date_filter,
                    "-",
                    "-",
                    "-",
                    "Absent"
                ))
        else:
            data = self.controller.db.get_attendance_reports(date_filter)
            for row in data:
                self.tree.insert("", "end", values=(
                    row.get("student_id"),
                    row.get("name"),
                    row.get("date"),
                    row.get("time"),
                    row.get("subject", "-"),
                    row.get("time_slot", "-"),
                    row.get("status")
                ))

    def get_dataframe(self):
        # We need to respect the filter? The original implementation exported ALL data regardless of filter view logic usually. 
        # But usually WYSIWYG is better. Let's export what's visible or all?
        # The user's original logic exported ALL. Let's stick to ALL for consistency unless asked.
        data = self.controller.db.get_attendance_reports() 
        if not data:
            return None
        return pd.DataFrame(data)

    def export_csv(self):
        df = self.get_dataframe()
        if df is None or df.empty:
            messagebox.showwarning("No Data", "No attendance records to export.")
            return
            
        filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if filename:
            try:
                df.to_csv(filename, index=False)
                messagebox.showinfo("Success", "Exported to CSV successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {e}")

    def export_excel(self):
        df = self.get_dataframe()
        if df is None or df.empty:
            messagebox.showwarning("No Data", "No attendance records to export.")
            return

        filename = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")])
        if filename:
            try:
                df.to_excel(filename, index=False)
                messagebox.showinfo("Success", "Exported to Excel successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {e}")
