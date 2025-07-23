import sqlite3
from datetime import datetime
from typing import List, Dict

DB_PATH = '/workspaces/nutflix-platform/nutflix.db'

# Helper to get top N recent sightings from clip_metadata
def get_recent_sightings(limit=100) -> List[Dict]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute('''
        SELECT timestamp, species, behavior, confidence, camera, motion_zone, clip_path
        FROM clip_metadata
        WHERE species IS NOT NULL AND species != ''
        ORDER BY timestamp DESC
        LIMIT ?
    ''', (limit,))
    rows = cur.fetchall()
    conn.close()
    # Format timestamp for display
    results = []
    for row in rows:
        ts = row['timestamp']
        try:
            dt = datetime.fromisoformat(ts)
            ts_fmt = dt.strftime('%B %d, %Y %I:%M %p')
        except Exception:
            ts_fmt = ts
        results.append({
            'species': row['species'],
            'behavior': row['behavior'],
            'confidence': row['confidence'],
            'camera': row['camera'],
            'motion_zone': row['motion_zone'],
            'clip_path': row['clip_path'],
            'timestamp': ts_fmt
        })
    return results

# Helper to get latest N environment readings for trends chart
def get_recent_env_readings(limit=200) -> Dict:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute('''
        SELECT timestamp, temperature, humidity, pressure
        FROM environment_readings
        ORDER BY timestamp DESC
        LIMIT ?
    ''', (limit,))
    rows = cur.fetchall()
    conn.close()
    # Reverse to ascending order for chart
    rows = list(rows)[::-1]
    labels = []
    temperature = []
    humidity = []
    pressure = []
    for row in rows:
        ts = row['timestamp']
        try:
            dt = datetime.fromisoformat(ts)
            label = dt.strftime('%I:%M %p')
        except Exception:
            label = ts
        labels.append(label)
        temperature.append(row['temperature'])
        humidity.append(row['humidity'])
        pressure.append(row['pressure'])
    return {
        'labels': labels,
        'temperature': temperature,
        'humidity': humidity,
        'pressure': pressure,
        'count': len(labels)
    }
