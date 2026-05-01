import customtkinter as ctk
import threading
from utils.face_recognizer import FaceRecognizer
from PIL import Image

class TrainPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Center Content
        self.center_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.center_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Icon (Optional, if available)
        # self.icon_lbl = ctk.CTkLabel(self.center_frame, text="", image=...)
        # self.icon_lbl.pack(pady=20)
        
        self.label = ctk.CTkLabel(self.center_frame, text="Train Face Recognition Model", 
                                  font=ctk.CTkFont(family="Roboto", size=26, weight="bold"))
        self.label.pack(pady=(0, 20))
        
        self.desc = ctk.CTkLabel(self.center_frame, 
                                 text="Click below to train the model with the latest student data.\nThis process updates the recognition engine to include new registrations.",
                                 font=("Roboto", 14), text_color="gray70")
        self.desc.pack(pady=(0, 40))
        
        self.train_btn = ctk.CTkButton(self.center_frame, text="START TRAINING", 
                                       command=self.start_training, 
                                       width=250, height=50,
                                       font=ctk.CTkFont(size=15, weight="bold"),
                                       fg_color="#3B8ED0", hover_color="#1F6AA5")
        self.train_btn.pack(pady=10)
        
        self.status_label = ctk.CTkLabel(self.center_frame, text="Status: Ready", 
                                         font=("Roboto", 14), text_color="gray")
        self.status_label.pack(pady=20)
        
        self.progress = ctk.CTkProgressBar(self.center_frame, width=400, height=15)
        self.progress.pack(pady=10)
        self.progress.set(0)
        
        # Hidden initially
        self.progress.pack_forget()

    def start_training(self):
        self.train_btn.configure(state="disabled", text="TRAINING...")
        self.status_label.configure(text="Status: Initializing...", text_color="orange")
        self.progress.pack(pady=10) # Show progress bar
        self.progress.start()
        
        threading.Thread(target=self.run_training, daemon=True).start()
        
    def run_training(self):
        recognizer = FaceRecognizer()
        # Ensure we catch errors
        try:
            success = recognizer.train_model(progress_callback=self.update_status)
        except Exception as e:
            success = False
            self.update_status(f"Error: {str(e)}")
        
        self.after(0, lambda: self.training_complete(success))
            
    def training_complete(self, success):
        self.progress.stop()
        self.progress.pack_forget()
        self.train_btn.configure(state="normal", text="START TRAINING")
        
        if success:
            self.status_label.configure(text="Status: Training Completed Successfully!", text_color="#2CC985") # Green
            messagebox = self.controller.messagebox if hasattr(self.controller, 'messagebox') else None
            # Or just use CTkMessagebox if installed, or standard messagebox
            from tkinter import messagebox
            messagebox.showinfo("Success", "Model trained successfully!")
        else:
            self.status_label.configure(text="Status: Training Failed.", text_color="#e74c3c") # Red

    def update_status(self, msg):
        self.status_label.configure(text=f"Status: {msg}")
