import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'desktop_app')))

from database.db import Database
from datetime import datetime

db = Database()

print("--- DEBUG MANUAL SESSION ---")

# 1. Get Current Config
conf = db.get_config()
print(f"Current Config Manual ID: {conf.get('manual_session_id')}")

# 2. Get Active Class (Before Limit)
active = db.get_active_class()
print(f"Active Class (Before): {active['subject'] if active else 'None'}")

# 3. Pick a random class to set as manual
timetables = db.get_timetables()
if not timetables:
    print("No timetables found to test.")
    sys.exit()

target = timetables[0]
target_id = str(target['_id'])
print(f"Setting Manual Session to: {target['subject']} (ID: {target_id})")

# 4. Set Manual
db.set_manual_session(target_id)

# 5. Check Config Again
conf = db.get_config()
print(f"Config Manual ID After Set: {conf.get('manual_session_id')}")

# 6. Check Active Class (After)
active = db.get_active_class()
if active:
    print(f"Active Class (After): {active['subject']}")
    print(f"Is Manual Flag: {active.get('is_manual')}")
    
    if str(active['_id']) == target_id:
        print("SUCCESS: Manual session is active and matches target.")
    else:
        print("FAILURE: Active class does not match target.")
else:
    print("FAILURE: No active class returned after setting manual.")

# 7. Clear Manual
db.clear_manual_session()
conf = db.get_config()
print(f"Config Manual ID After Clear: {conf.get('manual_session_id')}")

print("--- END DEBUG ---")
