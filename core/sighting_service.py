"""
Real-time sighting service that connects motion detection to database storage
"""
import sqlite3
import time
from datetime import datetime
from typing import Dict, Optional
import threading
import json
import os

# Core imports
from core.motion.motion_detector import MotionDetector
from core.camera.camera_manager import CameraManager
from core.storage.file_manager import FileManager

DB_PATH = '/home/p12146/NutFlix/nutflix-platform/nutflix.db'

class SightingService:
    def __init__(self):
        self.db_path = DB_PATH
        self.motion_detector = None
        self.camera_manager = None
        self.file_manager = None
        self.running = False
        self.recent_sightings = []  # In-memory cache for quick access
        self.sighting_callbacks = []  # For real-time updates
        
        # Initialize database
        self._init_database()
        
    def _init_database(self):
        """Initialize database tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        # Create clip_metadata table if it doesn't exist
        cur.execute('''
            CREATE TABLE IF NOT EXISTS clip_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                species TEXT,
                behavior TEXT,
                confidence REAL,
                camera TEXT,
                motion_zone TEXT,
                clip_path TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create motion_events table for raw motion data
        cur.execute('''
            CREATE TABLE IF NOT EXISTS motion_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                camera TEXT,
                motion_type TEXT,  -- 'gpio' or 'vision'
                confidence REAL,
                duration REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def start_detection(self):
        """Start the motion detection and sighting system"""
        if self.running:
            return
            
        self.running = True
        
        # Initialize components
        try:
            # Initialize motion detector with default config
            sensor_config = {
                'CritterCam': 18,  # Default GPIO pin
                'NestCam': 19
            }
            self.motion_detector = MotionDetector(sensor_config)
            # Skip FileManager for now - we'll implement clip saving later
            self.file_manager = None
            
            # Set up motion detection callback
            self.motion_detector.set_motion_callback(self._on_motion_detected)
            
            # Start motion detection
            self.motion_detector.start_detection()
            
            print("✅ Sighting service started - motion detection active")
            
        except Exception as e:
            print(f"❌ Error starting sighting service: {e}")
            self.running = False
            
    def stop_detection(self):
        """Stop the motion detection system"""
        self.running = False
        
        if self.motion_detector:
            self.motion_detector.stop_detection()
            
        print("🛑 Sighting service stopped")
        
    def _on_motion_detected(self, motion_data: Dict):
        """Callback when motion is detected"""
        try:
            # Get current timestamp
            timestamp = datetime.now().isoformat()
            
            # Determine species based on motion characteristics
            species = self._classify_motion(motion_data)
            
            # Record motion event
            self._record_motion_event(timestamp, motion_data)
            
            # Create sighting entry
            sighting = self._create_sighting(timestamp, species, motion_data)
            
            # Add to cache
            self.recent_sightings.insert(0, sighting)
            if len(self.recent_sightings) > 100:
                self.recent_sightings = self.recent_sightings[:100]
                
            # Notify callbacks (for real-time updates)
            self._notify_sighting_callbacks(sighting)
            
            print(f"🐿️ New sighting recorded: {species} at {timestamp}")
            
        except Exception as e:
            print(f"❌ Error processing motion detection: {e}")
            
    def _classify_motion(self, motion_data: Dict) -> str:
        """Simple motion classification - can be enhanced with AI later"""
        motion_type = motion_data.get('type', 'unknown')
        duration = motion_data.get('duration', 0)
        
        # Simple heuristics for now
        if motion_type == 'gpio':
            if duration > 5:
                return "Human"  # Longer duration suggests human
            else:
                return "Squirrel"  # Quick movement
        elif motion_type == 'vision':
            # Could analyze frame data here for better classification
            return "Wildlife"
        else:
            return "Unknown Motion"
            
    def _record_motion_event(self, timestamp: str, motion_data: Dict):
        """Record raw motion event in database"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        cur.execute('''
            INSERT INTO motion_events (timestamp, camera, motion_type, confidence, duration)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            timestamp,
            motion_data.get('camera', 'unknown'),
            motion_data.get('type', 'unknown'),
            motion_data.get('confidence', 0.0),
            motion_data.get('duration', 0.0)
        ))
        
        conn.commit()
        conn.close()
        
    def _create_sighting(self, timestamp: str, species: str, motion_data: Dict) -> Dict:
        """Create and store a sighting record"""
        # Determine behavior based on motion data
        behavior = self._determine_behavior(motion_data)
        
        # Calculate confidence
        confidence = motion_data.get('confidence', 0.8)
        
        # Get camera info
        camera = motion_data.get('camera', 'Camera 1')
        
        # Motion zone
        motion_zone = motion_data.get('zone', 'center')
        
        # For now, no clip path - could be added later
        clip_path = None
        
        # Store in database
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        cur.execute('''
            INSERT INTO clip_metadata (timestamp, species, behavior, confidence, camera, motion_zone, clip_path)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            timestamp, species, behavior, confidence, camera, motion_zone, clip_path
        ))
        
        conn.commit()
        conn.close()
        
        # Format for display
        try:
            dt = datetime.fromisoformat(timestamp)
            ts_fmt = dt.strftime('%B %d, %Y %I:%M %p')
        except Exception:
            ts_fmt = timestamp
            
        return {
            'species': species,
            'behavior': behavior,
            'confidence': confidence,
            'camera': camera,
            'motion_zone': motion_zone,
            'clip_path': clip_path,
            'timestamp': ts_fmt,
            'raw_timestamp': timestamp
        }
        
    def _determine_behavior(self, motion_data: Dict) -> str:
        """Determine behavior from motion characteristics"""
        motion_type = motion_data.get('type', 'unknown')
        duration = motion_data.get('duration', 0)
        
        if motion_type == 'gpio':
            if duration > 10:
                return "investigating"
            elif duration > 3:
                return "foraging"
            else:
                return "passing"
        else:
            return "active"
            
    def add_sighting_callback(self, callback):
        """Add callback for real-time sighting updates"""
        self.sighting_callbacks.append(callback)
        
    def _notify_sighting_callbacks(self, sighting: Dict):
        """Notify all registered callbacks of new sighting"""
        for callback in self.sighting_callbacks:
            try:
                callback(sighting)
            except Exception as e:
                print(f"❌ Error in sighting callback: {e}")
                
    def get_recent_sightings(self, limit: int = 10) -> list:
        """Get recent sightings from database"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        cur.execute('''
            SELECT timestamp, species, behavior, confidence, camera, motion_zone, clip_path
            FROM clip_metadata
            ORDER BY created_at DESC
            LIMIT ?
        ''', (limit,))
        
        rows = cur.fetchall()
        conn.close()
        
        # Format results
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
                'timestamp': ts_fmt,
                'raw_timestamp': ts
            })
            
        return results
        
    def get_sighting_stats(self) -> Dict:
        """Get sighting statistics"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        # Total sightings today
        today = datetime.now().strftime('%Y-%m-%d')
        cur.execute('''
            SELECT COUNT(*) as count FROM clip_metadata 
            WHERE timestamp LIKE ?
        ''', (f'{today}%',))
        today_count = cur.fetchone()[0]
        
        # Most common species
        cur.execute('''
            SELECT species, COUNT(*) as count 
            FROM clip_metadata 
            WHERE species IS NOT NULL 
            GROUP BY species 
            ORDER BY count DESC 
            LIMIT 1
        ''')
        common_result = cur.fetchone()
        most_common = common_result[0] if common_result else "None"
        
        conn.close()
        
        return {
            'total_today': today_count,
            'most_common_species': most_common,
            'detection_active': self.running
        }

# Global sighting service instance
sighting_service = SightingService()
