import customtkinter as ctk
from tkinter import messagebox
from PIL import Image

class LoginPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        self.configure(fg_color="transparent")
        
        # Background Image (Optional - can be added later)
        
        # Center Box (Card Design)
        self.center_frame = ctk.CTkFrame(self, width=400, height=450, corner_radius=20, fg_color="#2b2b2b")
        self.center_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.center_frame.pack_propagate(False) # Prevent shrinking
        
        # Header
        self.label = ctk.CTkLabel(self.center_frame, text="Admin Login", font=ctk.CTkFont(family="Roboto", size=28, weight="bold"))
        self.label.pack(pady=(50, 30))
        
        # Username Field
        self.user_entry = ctk.CTkEntry(self.center_frame, placeholder_text="Username", width=280, height=40, font=("Roboto", 14))
        self.user_entry.pack(pady=15)
        
        # Password Field
        self.pass_entry = ctk.CTkEntry(self.center_frame, placeholder_text="Password", show="*", width=280, height=40, font=("Roboto", 14))
        self.pass_entry.pack(pady=15)
        
        # Login Button
        self.login_btn = ctk.CTkButton(self.center_frame, text="LOGIN", width=280, height=45, 
                                       font=ctk.CTkFont(family="Roboto", size=15, weight="bold"),
                                       fg_color="#3B8ED0", hover_color="#1F6AA5",
                                       command=self.login)
        self.login_btn.pack(pady=40)
        
        # Footer
        self.footer = ctk.CTkLabel(self.center_frame, text="Smart Attendance System v2.0", font=("Roboto", 10), text_color="gray")
        self.footer.pack(side="bottom", pady=15)
        
    def login(self):
        username = self.user_entry.get()
        password = self.pass_entry.get()
        
        if self.controller.db.verify_admin(username, password):
            self.controller.show_dashboard()
        else:
            self.user_entry.delete(0, 'end')
            self.pass_entry.delete(0, 'end')
            self.user_entry.configure(placeholder_text_color="red")
            messagebox.showerror("Login Failed", "Invalid Credentials")
