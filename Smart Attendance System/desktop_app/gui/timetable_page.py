import customtkinter as ctk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime

class TimetablePage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Layout: Top (Add Form), Bottom (List)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # --- Header ---
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=10)
        
        ctk.CTkLabel(self.header_frame, text="Timetable Management", font=ctk.CTkFont(size=24, weight="bold")).pack(side="left")
        
        self.btn_refresh = ctk.CTkButton(self.header_frame, text="Refresh", width=80, command=self.load_data, fg_color="#2CC985")
        self.btn_refresh.pack(side="right", padx=10)

        # --- Add Class Form (Collapsible or just visible) ---
        self.form_frame = ctk.CTkFrame(self)
        self.form_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=5)
        
        # Row 1: Day, Start (Time + AM/PM), End (Time + AM/PM)
        self.day_var = ctk.StringVar(value="Monday")
        self.days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        ctk.CTkOptionMenu(self.form_frame, variable=self.day_var, values=self.days, width=110).grid(row=0, column=0, padx=5, pady=5)
        
        # Start Time Frame
        self.start_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        self.start_frame.grid(row=0, column=1, padx=5, pady=5)
        self.start_time = ctk.CTkEntry(self.start_frame, placeholder_text="HH:MM", width=60)
        self.start_time.pack(side="left", padx=2)
        self.start_ampm = ctk.CTkOptionMenu(self.start_frame, values=["AM", "PM"], width=60)
        self.start_ampm.pack(side="left", padx=2)
        
        # End Time Frame
        self.end_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        self.end_frame.grid(row=0, column=2, padx=5, pady=5)
        self.end_time = ctk.CTkEntry(self.end_frame, placeholder_text="HH:MM", width=60)
        self.end_time.pack(side="left", padx=2)
        self.end_ampm = ctk.CTkOptionMenu(self.end_frame, values=["AM", "PM"], width=60)
        self.end_ampm.pack(side="left", padx=2)
        
        # Row 2: Subject, Faculty, Section, Add Button
        self.subject = ctk.CTkEntry(self.form_frame, placeholder_text="Subject Name", width=140)
        self.subject.grid(row=0, column=3, padx=5, pady=5)
        
        self.faculty = ctk.CTkEntry(self.form_frame, placeholder_text="Faculty (Opt)", width=110)
        self.faculty.grid(row=0, column=4, padx=5, pady=5)

        self.btn_add = ctk.CTkButton(self.form_frame, text="+ Add Class", width=100, command=self.add_class)
        self.btn_add.grid(row=0, column=5, padx=10, pady=5)

        # --- Table Area ---
        self.table_frame = ctk.CTkFrame(self)
        self.table_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        self.grid_rowconfigure(2, weight=1) # Make table expand
        
        # Treeview
        columns = ("ID", "Day", "Start", "End", "Subject", "Faculty")
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings", selectmode="browse")
        
        # Style
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2b2b2b", foreground="white", fieldbackground="#2b2b2b", rowheight=30, borderwidth=0)
        style.map('Treeview', background=[('selected', '#3B8ED0')])
        style.configure("Treeview.Heading", background="#212121", foreground="white", font=("Roboto", 10, "bold"))
        
        # Headings
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100 if col != "ID" else 0, stretch=True) # ID hiddenish
            
        self.tree.column("ID", width=0, stretch=False) # Hide ID
        
        # Scrollbars
        vsb = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        vsb.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(fill="both", expand=True)
        
        # Actions
        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.grid(row=3, column=0, pady=10, padx=20, sticky="ew")
        
        self.btn_delete = ctk.CTkButton(action_frame, text="Delete Selected", fg_color="#FF4C4C", hover_color="#C43B3B", command=self.delete_selected)
        self.btn_delete.pack(side="right", padx=5)
        
        self.load_data()

    def add_class(self):
        day = self.day_var.get()
        start = self.start_time.get().strip()
        end = self.end_time.get().strip()
        start_ampm = self.start_ampm.get()
        end_ampm = self.end_ampm.get()
        sub = self.subject.get().strip()
        fac = self.faculty.get().strip()
        
        if not start or not end or not sub:
            messagebox.showerror("Error", "Start Time, End Time, and Subject are required!")
            return
            
        # Basic validation
        try:
            # Parse 12-hour format
            s_dt = datetime.strptime(f"{start} {start_ampm}", "%I:%M %p")
            e_dt = datetime.strptime(f"{end} {end_ampm}", "%I:%M %p")
            
            # Normalize to 24-hour format (HH:MM) for DB
            start = s_dt.strftime("%H:%M")
            end = e_dt.strftime("%H:%M")
        except ValueError:
            messagebox.showerror("Error", "Time must be in HH:MM format (12h)!")
            return
            
        success, msg = self.controller.db.add_timetable_entry(day, start, end, sub, fac)
        if success:
            self.load_data()
            self.subject.delete(0, 'end')
            # self.start_time.delete(0, 'end') # Keep times for easier consecutive entry? Maybe.
        else:
            messagebox.showerror("Error", msg)

    def load_data(self):
        # Clear
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Fetch
        data = self.controller.db.get_timetables()
        
        for entry in data:
            self.tree.insert("", "end", values=(
                str(entry["_id"]),
                entry["day"],
                entry["start_time"],
                entry["end_time"],
                entry["subject"],
                entry.get("faculty", "")
            ))

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            return
        
        item = self.tree.item(selected[0])
        entry_id = item['values'][0]
        
        if messagebox.askyesno("Confirm", "Delete this class schedule?"):
            self.controller.db.delete_timetable_entry(entry_id)
            self.load_data()


