import os
import sys

# Ensure project root is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gui.attendance_app import AttendanceApp

if __name__ == "__main__":
    app = AttendanceApp()
    app.mainloop()
