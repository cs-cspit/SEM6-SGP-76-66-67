import os
import sys

# Ensure project root is in path to allow imports if needed, though mostly local imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gui.app_gui import SmartAttendanceApp

if __name__ == "__main__":
    app = SmartAttendanceApp()
    app.mainloop()
