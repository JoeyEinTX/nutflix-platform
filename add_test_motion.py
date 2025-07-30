#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')
import sqlite3
from datetime import datetime

# Add a test motion event to see if the Flask server can read it
conn = sqlite3.connect('nutflix.db')
cur = conn.cursor()

timestamp = datetime.now().isoformat()
cur.execute('''
    INSERT INTO motion_events (timestamp, camera, motion_type, confidence, duration)
    VALUES (?, ?, ?, ?, ?)
''', (timestamp, 'CritterCam', 'gpio', 0.95, 3.0))

conn.commit()
print(f"✅ Added test motion event to motion_events table:")
print(f"   Time: {timestamp}")
print(f"   Camera: CritterCam")
print(f"   Type: gpio (PIR sensor)")
print(f"   Confidence: 0.95")

conn.close()
print("\n🔍 Check your dashboard - this should appear in Recent Sightings!")
