import customtkinter as ctk
from tkinter import ttk
import tkinter as tk
from PIL import Image, ImageTk
import os

class StudentView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Grid Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0) # Right panel for photo
        self.grid_rowconfigure(1, weight=1)
        
        # Header / Control Bar
        self.control_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.control_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        ctk.CTkLabel(self.control_frame, text="Student Management", font=ctk.CTkFont(size=24, weight="bold")).pack(side="left")
        
        self.refresh_btn = ctk.CTkButton(self.control_frame, text="Refresh", width=80, command=self.load_data, fg_color="#2CC985", hover_color="#219a64")
        self.refresh_btn.pack(side="right", padx=5)
        
        # Filter: Department
        self.dept_var = ctk.StringVar(value="Department: All")
        self.dept_menu = ctk.CTkOptionMenu(self.control_frame, variable=self.dept_var, values=["Department: All", "CSE", "ECE", "MECH", "CIVIL", "AI&DS"], command=self.apply_filters, width=150)
        self.dept_menu.pack(side="right", padx=5)

        # Filter: Year
        self.year_var = ctk.StringVar(value="Year: All")
        self.year_menu = ctk.CTkOptionMenu(self.control_frame, variable=self.year_var, values=["Year: All", "1st", "2nd", "3rd", "4th"], command=self.apply_filters, width=120)
        self.year_menu.pack(side="right", padx=5)

        # ---------------- Table Area ----------------
        self.tree_frame = ctk.CTkFrame(self)
        self.tree_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        
        # Style Treeview
        style = ttk.Style()
        style.theme_use("clam")
        
        # Colors
        bg_color = "#2b2b2b"
        text_color = "white"
        selected_color = "#3B8ED0"
        
        style.configure("Treeview", 
                        background=bg_color, 
                        foreground=text_color, 
                        fieldbackground=bg_color, 
                        rowheight=35,
                        font=("Roboto", 11),
                        borderwidth=0)
        style.configure("Treeview.Heading", background="#212121", foreground="white", relief="flat", font=("Roboto", 12, "bold"))
        style.map('Treeview', background=[('selected', selected_color)])
        
        columns = ("ID", "Name", "Department", "Year", "Email", "Mobile", "PhotoID")
        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings", selectmode="browse")
        
        # Scrollbars (CustomTkinter doesn't support scrollbar for Tk widget directly roughly, use ctk scrollbar if possible or standard)
        # Using standard ttk scrollbar with dark style is hard. 
        # Trick: Use CTkScrollbar? No, it works with CTkScrollableFrame. 
        # Standard Scrollbar:
        self.vsb = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.hsb = ttk.Scrollbar(self.tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=self.vsb.set, xscrollcommand=self.hsb.set)
        
        self.vsb.pack(side="right", fill="y")
        self.hsb.pack(side="bottom", fill="x")
        self.tree.pack(fill="both", expand=True)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor="w")
            
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        
        # ---------------- Photo Preview Panel ----------------
        self.info_panel = ctk.CTkFrame(self, width=250, corner_radius=15)
        self.info_panel.grid(row=1, column=1, sticky="nsew")
        self.info_panel.grid_propagate(False) # Keep fixed width
        
        ctk.CTkLabel(self.info_panel, text="Student Photo", font=("Roboto", 16, "bold")).pack(pady=20)
        
        self.photo_label = ctk.CTkLabel(self.info_panel, text="", width=200, height=200, fg_color="#1a1a1a", corner_radius=10)
        self.photo_label.pack(pady=10, padx=20)
        
        self.student_name_lbl = ctk.CTkLabel(self.info_panel, text="Select a student", font=("Roboto", 14), wraplength=230)
        self.student_name_lbl.pack(pady=10)
        
        self.load_data()
        
    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        students = self.controller.db.get_all_students()
        
        dept_filter = self.dept_var.get().replace("Department: ", "")
        year_filter = self.year_var.get().replace("Year: ", "")
        
        for s in students:
            if dept_filter != "All" and s.get('department') != dept_filter:
                continue
            if year_filter != "All" and s.get('year') != year_filter:
                continue
                
            self.tree.insert("", "end", values=(
                s.get("student_id"),
                s.get("name"),
                s.get("department"),
                s.get("year"),
                s.get("email"),
                s.get("mobile"),
                s.get("image_path")
            ))

    def apply_filters(self, _):
        self.load_data()
        
    def on_select(self, event):
        selected = self.tree.focus()
        if selected:
            values = self.tree.item(selected, 'values')
            if values:
                img_path = values[6] 
                name = values[1]
                self.student_name_lbl.configure(text=name)
                self.show_photo(img_path)

    def show_photo(self, rel_path):
        import os
        try:
             full_path = os.path.join(os.getcwd(), rel_path)
             if not os.path.exists(full_path):
                 full_path = os.path.join(os.getcwd(), "..", rel_path)
             
             if os.path.exists(full_path):
                 img = Image.open(full_path)
                 # Resize keeping aspect ratio
                 ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(180, 180))
                 self.photo_label.configure(image=ctk_img, text="")
             else:
                 self.photo_label.configure(text="Image Not Found", image=None)
        except Exception as e:
            print(f"Error loading image: {e}")
            self.photo_label.configure(text="Error", image=None)
