import os
import time
import cv2
import numpy as np
import base64
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from pymongo import MongoClient
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "secret_key_attendance_system"  # Change this in production
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB Limit for uploads

# --- Configuration ---
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "smart_attendance_db"
DATASET_DIR = os.path.join(os.getcwd(), "..", "dataset")  # Stored in parent dataset/ folder

# --- Database Connection ---
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
students_collection = db["students"]

# --- Helpers ---
def detect_face(image_path):
    """
    Checks if the uploaded image contains exactly one face using OpenCV Haar Cascades.
    Returns True if valid, False otherwise.
    """
    try:
        # Load the cascade
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        img = cv2.imread(image_path)
        if img is None:
            return False
            
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        # Valid if at least 1 face is found
        if len(faces) > 0:
            return True
        return False
    except Exception as e:
        print(f"Error in face detection: {e}")
        return False

# --- Routes ---

# Ensure desktop_app is importable
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'desktop_app'))

from utils.face_recognizer import FaceRecognizer
from database.db import db as desktop_db # Use the initialized DB from desktop app

# Initialize AI (Global)
recognizer = FaceRecognizer()

@app.route('/')
def home():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register():
    try:
        # 1. Get Form Data
        student_id = request.form['student_id']
        name = request.form['name']
        department = request.form['department']
        year = request.form['year']
        email = request.form['email']
        mobile = request.form['mobile']
        
        # 3. Image Handling (JSON List of ~30 images)
        import json
        images_json = request.form.get('images_json')
        if not images_json:
             flash("No image data received.", "danger")
             return redirect(url_for('home'))
             
        try:
            image_list = json.loads(images_json)
        except:
            flash("Invalid image data format.", "danger")
            return redirect(url_for('home'))

        if len(image_list) < 5:
            flash("Too few images captured. Please capture at least 5 frames.", "danger")
            return redirect(url_for('home'))

        # Create user directory in dataset
        user_dir = os.path.join(DATASET_DIR, student_id)
        os.makedirs(user_dir, exist_ok=True)
        
        saved_files = []
        valid_encodings = []
        valid_count = 0
        
        try:
            for idx, b64_str in enumerate(image_list):
                # Decode Base64
                if "," in b64_str:
                    header, encoded = b64_str.split(",", 1)
                else:
                    encoded = b64_str
                    
                data = base64.b64decode(encoded)
                nparr = np.frombuffer(data, np.uint8)
                cv_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                if cv_img is None: continue

                # 4. Attempt Detection & Encoding
                # We are lenient here: if one frame fails, we skip it.
                # We only need a good set of valid frames.
                encoding = recognizer.encode_single_image(cv_img)
                
                if encoding is not None:
                    # Save valid image
                    filename = f"frame_{idx}_{int(time.time())}.jpg"
                    save_path = os.path.join(user_dir, filename)
                    with open(save_path, "wb") as f:
                        f.write(data)
                    
                    saved_files.append(save_path)
                    valid_encodings.append(encoding)
                    valid_count += 1
            
            # Check if we have enough valid data
            if valid_count < 5:
                 raise Exception(f"Only {valid_count} valid faces detected out of {len(image_list)}. Please ensure your face is clearly visible and try again.")

            # 5. Save to MongoDB
            # Use the first valid image as the profile picture
            relative_image_path = f"dataset/{student_id}/{os.path.basename(saved_files[0])}"
            
            student_data = {
                "student_id": student_id,
                "name": name,
                "department": department,
                "year": year,
                "email": email,
                "mobile": mobile,
                "image_path": relative_image_path
            }
            
            # Insert student data
            students_collection.insert_one(student_data)
            
            # Save ALL Encodings
            desktop_db.update_student_encodings(student_id, valid_encodings)
            
            flash(f"Registration Successful! Saved {valid_count} valid face angles.", "success")
            return redirect(url_for('home'))
            
        except Exception as e:
            # Cleanup on failure
            for p in saved_files:
                if os.path.exists(p):
                    os.remove(p)
            try:
                os.rmdir(user_dir)
            except:
                pass
                
            flash(f"Registration Failed: {e}", "danger")
            print(f"Error: {e}")
            return redirect(url_for('home'))
            
    except Exception as e:
        print(e)
        flash(f"An error occurred: {e}", "danger")
        return redirect(url_for('home'))

if __name__ == '__main__':
    # Ensure dataset directory exists at root level
    os.makedirs(DATASET_DIR, exist_ok=True)
    app.run(debug=True, port=5000)
