@echo off
TITLE Smart Attendance System Launcher

:MENU
CLS
ECHO =========================================================
ECHO    SMART ATTENDANCE MANAGEMENT SYSTEM
ECHO =========================================================
ECHO.
ECHO    1. Install Dependencies
ECHO    2. Run Web App (Student Registration)
ECHO    3. Run Admin Desktop App (Login & Mgmt)
ECHO    4. Run Attendance Capture App (Standalone)
ECHO    5. Exit
ECHO.
SET /P M=Type 1, 2, 3, 4, or 5 then press ENTER: 

IF %M%==1 GOTO INSTALL
IF %M%==2 GOTO WEBAPP
IF %M%==3 GOTO DESKTOP
IF %M%==4 GOTO ATTENDANCE
IF %M%==5 GOTO EOF

:INSTALL
ECHO Installing dependencies...
pip install -r requirements.txt
PAUSE
GOTO MENU

:WEBAPP
ECHO Starting Web App...
ECHO Open http://127.0.0.1:5000 in your browser.
start http://127.0.0.1:5000
python web_app/app.py
PAUSE
GOTO MENU

:DESKTOP

ECHO Starting Admin Desktop App...
python desktop_app/main.py
PAUSE
GOTO MENU

:ATTENDANCE
ECHO Starting Attendance Capture App...
python desktop_app/attendance_main.py
PAUSE
GOTO MENU



Start mail sending app...
python daily_attendance_email.py
