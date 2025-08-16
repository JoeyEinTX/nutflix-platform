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

# Core imports - motion detection now handled by PIR sensors
from core.camera.camera_manager import CameraManager
from core.storage.file_manager import FileManager

# Smart IR LED controller
try:
    from core.infrared.smart_ir_controller import smart_ir_controller
    SMART_IR_AVAILABLE = True
    print("🔦 Smart IR controller integrated with sighting service")
except ImportError as e:
    print(f"⚠️ Smart IR controller not available: {e}")
    SMART_IR_AVAILABLE = False
    smart_ir_controller = None

DB_PATH = '/home/p12146/Projects/Nutflix-platform/nutflix.db'

class SightingService:
    def __init__(self):
        self.db_path = DB_PATH
        self.camera_manager = None  # Will be set from outside
        self.running = False
        self.recent_sightings = []  # In-memory cache for quick access
        self.sighting_callbacks = []  # For real-time updates
        
        # PIR sensors handle all motion detection - no camera monitoring needed
        
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
                thumbnail_path TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create motion_events table for raw motion data
        cur.execute('''
            CREATE TABLE IF NOT EXISTS motion_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                camera TEXT,
                motion_type TEXT  -- 'gpio' only (PIR sensors)
                confidence REAL,
                duration REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def start(self):
        """Start the sighting service (no camera motion detection - PIR only)"""
        if self.running:
            return
            
        self.running = True
        
        # PIR sensors handle all motion detection
        print("✅ Sighting service started - PIR motion detection only")
            
    def connect_camera_manager(self, camera_manager):
        """Connect an existing camera manager to avoid camera conflicts"""
        self.camera_manager = camera_manager
        
        # PIR sensors handle motion detection - no camera monitoring
        available_cameras = self.camera_manager.get_available_cameras()
        print(f"📹 Connected to cameras: {available_cameras}")
        print("📡 Motion detection: PIR sensors only")
        
    def stop_detection(self):
        """Stop the motion detection system"""
        self.running = False
            
        print("🛑 Sighting service stopped")
        
    def _start_camera_monitoring(self, camera_name: str):
        """Start monitoring a camera for motion in a separate thread"""
        import threading
        import time
        
        def monitor_camera():
            detector = self.motion_detectors[camera_name]
    def _classify_motion(self, motion_data: Dict) -> str:
        """Simple motion classification - can be enhanced with AI later"""
        motion_type = motion_data.get('type', 'unknown')
        duration = motion_data.get('duration', 0)
        camera = motion_data.get('camera', '').lower()
        
        # Camera-based classification as fallback for unknown motion types
        if 'nest' in camera:
            return "Squirrel"  # NestCam typically sees squirrels
        elif 'crit' in camera:
            return "Wildlife"  # CritterCam sees various critters
        
        # Duration-based heuristics for PIR sensors
        if motion_type == 'gpio':
            if duration > 5:
                return "Human"  # Longer duration suggests human
            else:
                return "Squirrel"  # Quick movement
        else:
            # For unknown motion types, use camera-based classification
            return "Wildlife"  # Default to wildlife for real motion events
            
    def _save_motion_thumbnail(self, camera_name: str, timestamp: str, frame) -> Optional[str]:
        """Save a thumbnail image for a motion detection event"""
        try:
            import cv2
            import os
            from pathlib import Path
            
            # Create thumbnails directory if it doesn't exist
            thumbnails_dir = Path("./thumbnails")
            thumbnails_dir.mkdir(exist_ok=True)
            
            # Generate filename based on camera and timestamp
            # Convert timestamp to safe filename format
            safe_timestamp = timestamp.replace(':', '-').replace('T', '_').split('.')[0]
            filename = f"{camera_name}_{safe_timestamp}.jpg"
            thumbnail_path = thumbnails_dir / filename
            
            # Convert frame to BGR if needed (for OpenCV)
            if len(frame.shape) == 3 and frame.shape[2] == 3:
                frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            else:
                frame_bgr = frame
            
            # Resize to thumbnail size (320x240 for good quality but manageable size)
            height, width = frame_bgr.shape[:2]
            thumb_width = 320
            thumb_height = int(height * (thumb_width / width))
            thumbnail = cv2.resize(frame_bgr, (thumb_width, thumb_height))
            
            # Add timestamp overlay
            cv2.putText(thumbnail, safe_timestamp, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(thumbnail, camera_name, (10, thumb_height - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Save thumbnail
            success = cv2.imwrite(str(thumbnail_path), thumbnail, [cv2.IMWRITE_JPEG_QUALITY, 85])
            
            if success:
                print(f"📸 Motion thumbnail saved: {thumbnail_path}")
                return str(thumbnail_path)
            else:
                print(f"❌ Failed to save thumbnail: {thumbnail_path}")
                return None
                
        except Exception as e:
            print(f"❌ Error saving motion thumbnail: {e}")
            return None
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
        
        # NEW: Check for clip that might be associated with this motion event
        print(f"📊 Motion event recorded: {motion_data.get('camera')} at {timestamp}")
    
    # NEW: Method to link clips with motion events
    def link_clip_to_recent_motion(self, camera_name: str, clip_path: str, thumbnail_path: str = None):
        """Link a recorded clip to the most recent motion event for this camera"""
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            
            # Find the most recent clip_metadata entry for this camera without a clip_path
            cur.execute('''
                SELECT id, timestamp FROM clip_metadata 
                WHERE camera = ? AND clip_path IS NULL 
                ORDER BY created_at DESC 
                LIMIT 1
            ''', (camera_name,))
            
            result = cur.fetchone()
            if result:
                clip_id, timestamp = result
                
                # Update the record with clip and thumbnail paths
                cur.execute('''
                    UPDATE clip_metadata 
                    SET clip_path = ?, thumbnail_path = ?
                    WHERE id = ?
                ''', (clip_path, thumbnail_path, clip_id))
                
                conn.commit()
                print(f"🔗 Linked clip to motion event: {camera_name} -> {clip_path}")
            else:
                print(f"⚠️ No recent motion event found to link clip: {camera_name}")
                
            conn.close()
            
        except Exception as e:
            print(f"❌ Error linking clip to motion event: {e}")
    
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
        
        # Get thumbnail path from motion data
        thumbnail_path = motion_data.get('thumbnail_path', None)
        
        # For now, no clip path - could be added later
        clip_path = None
        
        # Store in database
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        cur.execute('''
            INSERT INTO clip_metadata (timestamp, species, behavior, confidence, camera, motion_zone, clip_path, thumbnail_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            timestamp, species, behavior, confidence, camera, motion_zone, clip_path, thumbnail_path
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
            'thumbnail_path': thumbnail_path,
            'timestamp': ts_fmt,
            'raw_timestamp': timestamp
        }
        
    def _determine_behavior(self, motion_data: Dict) -> str:
        """Determine behavior from PIR motion characteristics"""
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
            
    def create_sighting_from_recording(self, camera_name: str, recording_metadata: Dict) -> Dict:
        """Create a sighting record from a PIR-triggered video recording"""
        try:
            # Extract information from recording metadata
            timestamp = recording_metadata.get('start_time', datetime.now().isoformat())
            filename = recording_metadata.get('filename', 'unknown.mp4')
            duration = recording_metadata.get('duration', 10.0)
            thumbnail_path = recording_metadata.get('thumbnail_path', None)
            trigger_type = recording_metadata.get('trigger_type', 'motion')
            
            # Create motion data for the PIR-triggered recording
            motion_data = {
                'camera': camera_name,
                'type': 'gpio',  # PIR-triggered recording
                'confidence': 0.95,  # High confidence for PIR-triggered clips
                'duration': duration,
                'zone': 'center',
                'last_motion_time': timestamp,
                'thumbnail_path': thumbnail_path,
                'clip_path': filename
            }
            
            # Determine species based on motion characteristics and camera
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
            
            print(f"🎬 PIR-triggered recording processed! New sighting: {species} on {camera_name} from clip {filename}")
            
            return sighting
            
        except Exception as e:
            print(f"❌ Error creating sighting from recording: {e}")
            return None

    def add_sighting_callback(self, callback):
        """Add callback for real-time sighting updates"""
        self.sighting_callbacks.append(callback)
        
    def _notify_sighting_callbacks(self, sighting: Dict):
        """Notify all registered callbacks of new sighting"""
        print(f"[SightingService] 🚀 Notifying {len(self.sighting_callbacks)} callbacks for {sighting.get('camera', 'unknown')} sighting")
        for callback in self.sighting_callbacks:
            try:
                callback(sighting)
            except Exception as e:
                print(f"❌ Error in sighting callback: {e}")
                
    def get_recent_sightings(self, limit: int = 10, camera: Optional[str] = None) -> list:
        """Get recent sightings from database, reading from clip_metadata table"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        # Read from clip_metadata to get thumbnail and clip paths
        if camera:
            cur.execute('''
                SELECT timestamp, camera, species, behavior, confidence, clip_path, thumbnail_path, created_at
                FROM clip_metadata
                WHERE camera = ?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (camera, limit))
        else:
            cur.execute('''
                SELECT timestamp, camera, species, behavior, confidence, clip_path, thumbnail_path, created_at
                FROM clip_metadata
                ORDER BY created_at DESC
                LIMIT ?
            ''', (limit,))
        
        rows = cur.fetchall()
        conn.close()
        
        # Format results to match expected sighting format
        results = []
        for row in rows:
            ts = row['timestamp']
            ts_fmt = ts
            if ts:
                try:
                    dt = datetime.fromisoformat(ts)
                    ts_fmt = dt.strftime('%B %d, %Y %I:%M %p')
                except Exception:
                    pass  # Leave ts_fmt as original string
            
            # Use data from clip_metadata table
            species = row['species'] or "Wildlife"
            behavior = row['behavior'] or "passing"
            camera_name = row['camera'] or 'Unknown'
            
            # Improve species classification if not set
            if species == "Wildlife":
                if 'nest' in camera_name.lower():
                    species = "Squirrel"  # NestCam typically sees squirrels
                
            results.append({
                'species': species,
                'behavior': behavior,
                'confidence': row['confidence'] or 0.95,
                'camera': row['camera'],
                'motion_zone': 'detected',
                'clip_path': row['clip_path'],
                'thumbnail_path': row['thumbnail_path'],
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
