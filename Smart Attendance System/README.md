# Smart Attendance Management System

A complete, production-ready system for managing student attendance using Face Recognition.
This project consists of two main components:
1.  **Web Application (Student)**: For self-registration and webcam photo capture.
2.  **Desktop Application (Admin)**: For managing records, training the AI model, and marking attendance via webcam.

---

## 🛠 Technology Stack
-   **Frontend:** HTML, CSS, JavaScript, CustomTkinter (Python GUI)
-   **Backend:** Python (Flask), OpenCV (Face Recognition)
-   **Database:** MongoDB

---

## 📂 Project Structure
```
SmartAttendanceSystem/
├── web_app/             # Student Registration Portal
│   ├── app.py           # Flask Backend
│   ├── templates/       # HTML Files
│   └── static/          # CSS Styles
├── desktop_app/         # Admin & Attendance System
│   ├── main.py          # Entry Point
│   ├── gui/             # UI Modules (Dashboard, Login, etc.)
│   ├── database/        # DB Connections
│   └── utils/           # Face Rec & Camera logic
├── dataset/             # Student Images (Auto-created)
├── models/              # Trained Face Models (Auto-created)
└── requirements.txt     # Dependencies
```

---

## 🚀 Setup & Installation

### 1. Prerequisites
-   Python 3.10+ installed.
-   MongoDB installed and running locally on port `27017` (Default).

### 2. Install Dependencies
Open a terminal in the project root (`SmartAttendanceSystem/`) and run:
```bash
pip install -r requirements.txt
```

---

## 🌐 Running the Web Application (Student Registration)
1.  Navigate to `web_app/`:
    ```bash
    cd web_app
    python app.py
    ```
2.  Open your browser and go to: `http://127.0.0.1:5000`
3.  Register a new student. **Capture a photo** using the webcam.
    -   The system will validate if a face is present.
    -   Images are saved to `dataset/` and details to MongoDB.

---

## 🖥 Running the Desktop Application (Admin & Attendance)
1.  Open a new terminal in the project root.
2.  Run the main application:
    ```bash
    python desktop_app/main.py
    ```
3.  **Login**:
    -   **Username:** `admin`
    -   **Password:** `admin123` (Default/First-time)

### Features:
-   **Students**: View all registered students, filter by Dept/Year, and preview photos.
-   **Train Model**:
    -   Go to "Train Model" tab.
    -   Click "Start Training".
    -   The system reads images from `dataset/`, trains the LBPH model, and saves it to `models/face_model.yml`.
    -   **IMPORTANT:** You MUST train the model after adding new students for them to be recognized.
-   **Mark Attendance**:
    -   Go to "Mark Attendance" tab.
    -   Click "Start Camera".
    -   The system will detect faces, match them, and mark attendance in MongoDB.
    -   It will freeze for 2 seconds upon a successful match to confirm.
-   **Reports**:
    -   View attendance logs.
    -   Export data to CSV or Excel.

---

## ⚠️ Troubleshooting
-   **No Module Named 'cv2'**: Ensure `opencv-contrib-python` is installed, not just `opencv-python`.
-   **Model not found**: You must run "Train Model" at least once.
-   **Database Error**: Ensure MongoDB service is running.

---
**Developed for Final Year Project / Industry Grade Implementation.**
