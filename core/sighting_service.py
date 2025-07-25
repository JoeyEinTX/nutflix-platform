"""
Real-time sighting service that connects motion detection to database storage
"""
import sqlite3
import time
import threading
from datetime import datetime
from typing import Dict, Optional
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
        self.camera_manager = None  # Will be set from outside
        self.running = False
        self.recent_sightings = []  # In-memory cache for quick access
        self.sighting_callbacks = []  # For real-time updates
        
        # Initialize motion detectors immediately
        self.motion_detectors = {
            'CritterCam': None,  # Will be initialized when needed
            'NestCam': None
        }
        self.motion_threads = {}
        
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
            # Import the VisionMotionDetector
            from core.motion.motion_detector import VisionMotionDetector
            
            # Initialize vision-based motion detectors
            self.motion_detectors['CritterCam'] = VisionMotionDetector(motion_sensitivity=0.3, cooldown_sec=2.0)
            self.motion_detectors['NestCam'] = VisionMotionDetector(motion_sensitivity=0.3, cooldown_sec=2.0)
            
            print("✅ Sighting service started - ready for vision-based motion detection")
            
        except Exception as e:
            print(f"❌ Error starting sighting service: {e}")
            self.running = False
            
    def connect_camera_manager(self, camera_manager):
        """Connect an existing camera manager to avoid camera conflicts"""
        self.camera_manager = camera_manager
        
        # Get available cameras
        available_cameras = self.camera_manager.get_available_cameras()
        print(f"📹 Connected to cameras: {available_cameras}")
        
        # Initialize VisionMotionDetectors if not already done
        if not self.running:
            from core.motion.motion_detector import VisionMotionDetector
            for camera_name in available_cameras:
                if camera_name in self.motion_detectors and self.motion_detectors[camera_name] is None:
                    self.motion_detectors[camera_name] = VisionMotionDetector(motion_sensitivity=0.3, cooldown_sec=2.0)
                    
        print("🎥 Vision-based motion detection connected and ready!")
        
    def check_motion_in_frame(self, camera_name: str, frame):
        """Check for motion in a frame (called from streaming service)"""
        if not self.running or camera_name not in self.motion_detectors:
            return False
            
        detector = self.motion_detectors[camera_name]
        if detector is None:
            # Initialize detector if not done yet
            from core.motion.motion_detector import VisionMotionDetector
            detector = VisionMotionDetector(motion_sensitivity=0.3, cooldown_sec=2.0)
            self.motion_detectors[camera_name] = detector
            
        motion_detected = detector.detect_motion(frame)
        
        if motion_detected:
            timestamp = datetime.now().isoformat()
            self._on_vision_motion_detected(camera_name, timestamp, detector)
            
        return motion_detected
            
    def stop_detection(self):
        """Stop the motion detection system"""
        self.running = False
        
        # Stop all camera monitoring threads
        for camera_name in list(self.motion_threads.keys()):
            self.motion_threads[camera_name] = False  # Signal thread to stop
            
        print("🛑 Sighting service stopped")
        
    def _start_camera_monitoring(self, camera_name: str):
        """Start monitoring a camera for motion in a separate thread"""
        import threading
        import time
        
        def monitor_camera():
            detector = self.motion_detectors[camera_name]
            self.motion_threads[camera_name] = True
            
            print(f"🎥 Starting motion monitoring for {camera_name}")
            
            while self.running and self.motion_threads.get(camera_name, False):
                try:
                    # Get current frame from camera
                    frame = self.camera_manager.get_frame(camera_name)
                    
                    # Check for motion
                    motion_detected = detector.detect_motion(frame)
                    
                    if motion_detected:
                        # Create motion event
                        timestamp = datetime.now().isoformat()
                        self._on_vision_motion_detected(camera_name, timestamp, detector)
                        
                    # Small delay to avoid overwhelming the system
                    time.sleep(0.5)  # Check for motion every 0.5 seconds
                    
                except Exception as e:
                    print(f"❌ Error monitoring {camera_name}: {e}")
                    time.sleep(1)  # Wait longer on error
                    
            print(f"🛑 Motion monitoring stopped for {camera_name}")
        
        # Start monitoring thread
        thread = threading.Thread(target=monitor_camera, daemon=True)
        thread.start()
        
    def _on_vision_motion_detected(self, camera_name: str, timestamp: str, detector):
        """Callback when vision-based motion is detected"""
        try:
            # Create motion data from vision detection
            last_motion = detector.get_last_motion_time()
            motion_data = {
                'camera': camera_name,
                'type': 'vision',
                'confidence': 0.90,  # High confidence for vision detection
                'duration': 3.0,     # Assume average duration
                'zone': 'center',
                'last_motion_time': last_motion.isoformat() if last_motion else timestamp
            }
            
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
            
            print(f"🐿️ Motion detected! New sighting: {species} on {camera_name} at {timestamp}")
            
        except Exception as e:
            print(f"❌ Error processing vision motion detection: {e}")
            
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
                
    def get_recent_sightings(self, limit: int = 10, camera: Optional[str] = None) -> list:
        """Get recent sightings from database, optionally filtered by camera"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        if camera:
            cur.execute('''
                SELECT timestamp, species, behavior, confidence, camera, motion_zone, clip_path
                FROM clip_metadata
                WHERE camera = ?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (camera, limit))
        else:
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
