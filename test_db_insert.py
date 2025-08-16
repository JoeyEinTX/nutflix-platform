#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')
import sqlite3
from datetime import datetime

# Add a test motion event
conn = sqlite3.connect('nutflix.db')
cur = conn.cursor()

timestamp = datetime.now().isoformat()
cur.execute('''
    INSERT INTO motion_events (timestamp, camera, motion_type, confidence, duration)
    VALUES (?, ?, ?, ?, ?)
''', (timestamp, 'CritterCam', 'gpio', 0.95, 2.3))

conn.commit()
print(f"✅ Added test motion event: {timestamp} - CritterCam - gpio")

# Show recent events
print("\n=== Recent Motion Events ===")
for row in cur.execute('SELECT timestamp, camera, motion_type FROM motion_events ORDER BY timestamp DESC LIMIT 3'):
    print(f"{row[0]} | {row[1]} | {row[2]}")

conn.close()
