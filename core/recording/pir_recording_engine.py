"""
PIR-Triggered Recording Engine v2.0
Complete end-to-end recording system for Nutflix platform
- PIR motion detection triggers recording
- Audio + Video recording with proper synchronization
- Thumbnail generation from recorded clips
- Database integration with proper linking
- Real file paths for dashboard display
"""

import os
import time
import threading
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
import subprocess
import sqlite3
import json
import numpy as np

try:
    from picamera2 import Picamera2
    from picamera2.encoders import H264Encoder, Quality
    from picamera2.outputs import FileOutput
    PICAMERA2_AVAILABLE = True
except ImportError:
    PICAMERA2_AVAILABLE = False
    print("⚠️ picamera2 not available - using mock recording")

try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    print("⚠️ OpenCV not available - thumbnail generation disabled")

try:
    import sounddevice as sd
    import numpy as np
    from scipy.io import wavfile
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    print("⚠️ Audio libraries not available - audio recording disabled")

from core.infrared.smart_ir_controller import SmartIRController

logger = logging.getLogger(__name__)

class PIRRecordingEngine:
    """Complete PIR-triggered recording system with audio/video sync and database integration"""
    
    def __init__(self, db_path='/home/p12146/Projects/Nutflix-platform/nutflix.db', camera_manager=None):
        self.db_path = db_path
        self.base_clips_dir = Path('/home/p12146/Projects/Nutflix-platform/clips')
        self.base_clips_dir.mkdir(exist_ok=True)
        
        # Camera manager reference for frame access
        self.camera_manager = camera_manager
        
        # Active recordings - tracks ongoing PIR-triggered sessions
        self.active_recordings: Dict[str, Dict[str, Any]] = {}
        self.recording_lock = threading.Lock()
        
        # IR controller for night vision
        try:
            self.ir_controller = SmartIRController()
        except Exception as e:
            logger.warning(f"⚠️ IR controller not available: {e}")
            self.ir_controller = None
        
        # Audio configuration
        self.audio_config = {
            'sample_rate': 16000,  # SPH0645 optimal rate
            'channels': 1,         # Mono
            'dtype': np.int16      # 16-bit audio
        }
        
        # Video configuration
        self.video_config = {
            'fps': 25,             # Standard 25fps
            'resolution': (1920, 1080),  # Full HD
            'quality': Quality.HIGH
        }
        
        # Recording settings
        self.min_duration = 10.0     # Minimum 10 seconds
        self.max_duration = 60.0     # Maximum 60 seconds
        self.grace_period = 3.0      # 3 seconds after PIR stops
        
        self._init_database()
        logger.info("🎬 PIRRecordingEngine initialized")
    
    def _init_database(self):
        """Initialize database tables for clip metadata"""
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            
            # Ensure clip_metadata table exists with all required fields
            cur.execute('''
                CREATE TABLE IF NOT EXISTS clip_metadata (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    species TEXT,
                    behavior TEXT,
                    confidence REAL,
                    camera TEXT NOT NULL,
                    motion_zone TEXT,
                    clip_path TEXT,
                    thumbnail_path TEXT,
                    duration REAL,
                    trigger_type TEXT DEFAULT 'pir_motion',
                    has_audio BOOLEAN DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Ensure motion_events table exists
            cur.execute('''
                CREATE TABLE IF NOT EXISTS motion_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    camera TEXT NOT NULL,
                    motion_type TEXT DEFAULT 'gpio',
                    confidence REAL DEFAULT 0.95,
                    duration REAL,
                    clip_id INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (clip_id) REFERENCES clip_metadata(id)
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("📊 Database tables initialized")
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
    
    def start_recording_from_pir(self, camera_name: str, motion_data: Dict) -> bool:
        """
        Start recording triggered by PIR motion detection
        
        Args:
            camera_name: 'NestCam' or 'CritterCam'
            motion_data: PIR motion event data
            
        Returns:
            bool: True if recording started successfully
        """
        with self.recording_lock:
            # Check if already recording for this camera
            if camera_name in self.active_recordings:
                # Extend existing recording
                self._extend_recording(camera_name, motion_data)
                return True
            
            try:
                # Create recording session
                timestamp = datetime.now()
                session_id = f"{camera_name}_{timestamp.strftime('%Y%m%d_%H%M%S')}"
                
                # Determine recording configuration
                has_audio = camera_name == 'NestCam' and AUDIO_AVAILABLE
                use_ir = self._should_use_ir(camera_name)
                
                # Create file paths
                date_dir = self.base_clips_dir / camera_name / timestamp.strftime('%Y-%m-%d')
                date_dir.mkdir(parents=True, exist_ok=True)
                
                base_filename = f"clip_{timestamp.strftime('%Y%m%d_%H%M%S')}"
                video_path = date_dir / f"{base_filename}.mp4"
                audio_path = date_dir / f"{base_filename}.wav" if has_audio else None
                thumbnail_path = date_dir / f"{base_filename}.jpg"
                
                # Create recording context
                recording_context = {
                    'session_id': session_id,
                    'camera_name': camera_name,
                    'start_time': timestamp,
                    'last_motion_time': timestamp,
                    'motion_data': motion_data,
                    'video_path': video_path,
                    'audio_path': audio_path,
                    'thumbnail_path': thumbnail_path,
                    'has_audio': has_audio,
                    'use_ir': use_ir,
                    'duration': 0.0,
                    'stop_event': threading.Event(),
                    'video_thread': None,
                    'audio_thread': None,
                    'ir_active': False
                }
                
                # Start recording threads
                success = self._start_recording_threads(recording_context)
                
                if success:
                    self.active_recordings[camera_name] = recording_context
                    logger.info(f"🎬 Started PIR recording for {camera_name} (audio: {has_audio}, IR: {use_ir})")
                    return True
                else:
                    logger.error(f"❌ Failed to start recording threads for {camera_name}")
                    return False
                    
            except Exception as e:
                logger.error(f"❌ Failed to start PIR recording for {camera_name}: {e}")
                return False
    
    def extend_recording_from_pir(self, camera_name: str, motion_data: Dict):
        """Extend existing recording when new PIR motion is detected"""
        with self.recording_lock:
            if camera_name in self.active_recordings:
                context = self.active_recordings[camera_name]
                context['last_motion_time'] = datetime.now()
                logger.info(f"⏰ Extended PIR recording for {camera_name}")
                return True
        return False
    
    def _extend_recording(self, camera_name: str, motion_data: Dict):
        """Internal method to extend recording"""
        if camera_name in self.active_recordings:
            context = self.active_recordings[camera_name]
            context['last_motion_time'] = datetime.now()
            logger.info(f"⏰ Extended recording for {camera_name}")
    
    def _should_use_ir(self, camera_name: str) -> bool:
        """Determine if IR LEDs should be used for recording"""
        if not self.ir_controller:
            return False
        
        # Use IR for low light conditions
        # For now, simple time-based logic (night hours)
        current_hour = datetime.now().hour
        is_night = current_hour < 7 or current_hour > 19
        
        return is_night
    
    def _start_recording_threads(self, context: Dict) -> bool:
        """Start video and audio recording threads"""
        try:
            # Start video recording thread
            video_thread = threading.Thread(
                target=self._video_recording_thread,
                args=(context,),
                daemon=True
            )
            context['video_thread'] = video_thread
            video_thread.start()
            
            # Start audio recording thread if needed
            if context['has_audio']:
                audio_thread = threading.Thread(
                    target=self._audio_recording_thread,
                    args=(context,),
                    daemon=True
                )
                context['audio_thread'] = audio_thread
                audio_thread.start()
            
            # Start monitoring thread to check for stop conditions
            monitor_thread = threading.Thread(
                target=self._recording_monitor_thread,
                args=(context,),
                daemon=True
            )
            monitor_thread.start()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start recording threads: {e}")
            return False
    
    def _video_recording_thread(self, context: Dict):
        """Video recording thread using shared camera manager"""
        camera_name = context['camera_name']
        video_path = context['video_path']
        
        try:
            # Activate IR if needed
            if context['use_ir'] and self.ir_controller:
                self.ir_controller.activate_for_camera(camera_name)
                context['ir_active'] = True
                logger.info(f"🔦 Activated IR LEDs for {camera_name}")
            
            # Use frame capture approach instead of direct camera access
            logger.info(f"📹 Starting frame-based video recording for {camera_name}: {video_path}")
            
            # Setup video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            fps = 20
            video_writer = None
            
            # Get actual frame dimensions from camera
            if self.camera_manager and hasattr(self.camera_manager, 'get_frame'):
                try:
                    test_frame = self.camera_manager.get_frame(camera_name)
                    if test_frame is not None and len(test_frame.shape) >= 2:
                        # Use actual frame dimensions (height, width)
                        actual_resolution = (test_frame.shape[1], test_frame.shape[0])
                        logger.info(f"📹 Using actual frame resolution: {actual_resolution}")
                    else:
                        actual_resolution = (640, 480)  # fallback
                        logger.warning(f"⚠️ Could not get test frame, using fallback resolution: {actual_resolution}")
                except Exception as e:
                    actual_resolution = (640, 480)  # fallback
                    logger.warning(f"⚠️ Error getting test frame, using fallback resolution: {actual_resolution}: {e}")
            else:
                actual_resolution = (640, 480)  # fallback
                logger.warning(f"⚠️ Camera manager not available, using fallback resolution: {actual_resolution}")
            
            if OPENCV_AVAILABLE:
                video_writer = cv2.VideoWriter(
                    str(video_path), 
                    fourcc, 
                    fps, 
                    actual_resolution
                )
            
            # Record frames until stop event
            start_time = datetime.now()
            frame_count = 0
            
            while not context['stop_event'].is_set():
                try:
                    # Get frame from camera manager if available
                    if self.camera_manager and hasattr(self.camera_manager, 'get_frame'):
                        frame = self.camera_manager.get_frame(camera_name)
                        
                        if frame is not None and video_writer is not None:
                            # Frame is already in BGR format from camera manager
                            if len(frame.shape) == 3 and frame.shape[2] == 3:
                                video_writer.write(frame)
                                frame_count += 1
                                if frame_count % 20 == 0:  # Log every 20 frames
                                    logger.debug(f"📹 Recorded {frame_count} frames for {camera_name}")
                            else:
                                logger.warning(f"⚠️ Invalid frame shape for {camera_name}: {frame.shape}")
                        elif frame is None:
                            logger.warning(f"⚠️ Got None frame from {camera_name}")
                        elif video_writer is None:
                            logger.warning(f"⚠️ Video writer not initialized for {camera_name}")
                        
                        # Sleep to maintain frame rate
                        time.sleep(1.0 / fps)
                    else:
                        # Fallback: just wait
                        time.sleep(0.1)
                    
                    # Update duration
                    context['duration'] = (datetime.now() - start_time).total_seconds()
                    
                    # Safety check for maximum duration
                    if context['duration'] > self.max_duration:
                        logger.warning(f"⏰ Maximum duration reached for {camera_name}")
                        break
                        
                except Exception as frame_error:
                    logger.warning(f"⚠️ Frame capture error for {camera_name}: {frame_error}")
                    time.sleep(0.1)
            
            # Close video writer
            if video_writer is not None:
                video_writer.release()
            
            logger.info(f"📹 Video recording completed: {video_path} ({context['duration']:.1f}s, {frame_count} frames)")
            
            # If we didn't get frames, create a minimal placeholder video
            if frame_count == 0 and context['duration'] > 0:
                logger.warning(f"⚠️ No frames captured, creating placeholder video for {camera_name}")
                self._create_placeholder_video(video_path, context['duration'])
            
        except Exception as e:
            logger.error(f"❌ Video recording failed for {camera_name}: {e}")
            # Create a very basic placeholder
            try:
                video_path.write_text(f"Recording failed for {camera_name}: {e}")
                logger.info(f"📝 Created error placeholder: {video_path}")
            except:
                pass
        
        finally:
            # Deactivate IR
            if context.get('ir_active') and self.ir_controller:
                self.ir_controller.deactivate_for_camera(camera_name)
                logger.info(f"🔦 Deactivated IR LEDs for {camera_name}")
    
    def _audio_recording_thread(self, context: Dict):
        """Audio recording thread using sounddevice"""
        camera_name = context['camera_name']
        audio_path = context['audio_path']
        
        if not AUDIO_AVAILABLE:
            logger.warning(f"🎤 Audio recording skipped for {camera_name} (libraries not available)")
            return
        
        try:
            logger.info(f"🎤 Audio recording started: {audio_path}")
            
            # Audio recording parameters
            samplerate = self.audio_config['sample_rate']
            channels = self.audio_config['channels']
            
            # Record audio frames
            frames = []
            
            def audio_callback(indata, frames_count, time, status):
                if status:
                    logger.warning(f"🎤 Audio status: {status}")
                frames.append(indata.copy())
            
            # Start audio stream
            with sd.InputStream(
                callback=audio_callback,
                samplerate=samplerate,
                channels=channels,
                dtype=self.audio_config['dtype']
            ):
                # Record until stop event
                while not context['stop_event'].is_set():
                    time.sleep(0.1)
            
            # Save audio file
            if frames:
                audio_data = np.concatenate(frames, axis=0)
                wavfile.write(str(audio_path), samplerate, audio_data)
                logger.info(f"🎤 Audio recording completed: {audio_path}")
            else:
                logger.warning(f"🎤 No audio data recorded for {camera_name}")
                
        except Exception as e:
            logger.error(f"❌ Audio recording failed for {camera_name}: {e}")
    
    def _recording_monitor_thread(self, context: Dict):
        """Monitor thread that decides when to stop recording"""
        camera_name = context['camera_name']
        
        try:
            while not context['stop_event'].is_set():
                time.sleep(0.5)  # Check every 500ms
                
                current_time = datetime.now()
                time_since_start = (current_time - context['start_time']).total_seconds()
                time_since_motion = (current_time - context['last_motion_time']).total_seconds()
                
                # Stop conditions:
                # 1. Minimum duration reached AND grace period after last motion
                # 2. Maximum duration reached
                should_stop = False
                
                if time_since_start >= self.min_duration and time_since_motion >= self.grace_period:
                    should_stop = True
                    logger.info(f"⏰ Stopping {camera_name} recording: grace period elapsed")
                
                if time_since_start >= self.max_duration:
                    should_stop = True
                    logger.info(f"⏰ Stopping {camera_name} recording: maximum duration reached")
                
                if should_stop:
                    context['stop_event'].set()
                    break
            
            # Wait for recording threads to complete
            if context['video_thread']:
                context['video_thread'].join(timeout=5.0)
            if context['audio_thread']:
                context['audio_thread'].join(timeout=5.0)
            
            # Post-processing
            self._finalize_recording(context)
            
        except Exception as e:
            logger.error(f"❌ Recording monitor failed for {camera_name}: {e}")
        
        finally:
            # Remove from active recordings
            with self.recording_lock:
                if camera_name in self.active_recordings:
                    del self.active_recordings[camera_name]
    
    def _finalize_recording(self, context: Dict):
        """Finalize recording: merge audio/video, generate thumbnail, update database"""
        camera_name = context['camera_name']
        
        try:
            # Step 1: Merge audio and video if both exist
            final_video_path = self._merge_audio_video(context)
            
            # Step 2: Generate thumbnail
            thumbnail_success = self._generate_thumbnail(final_video_path, context['thumbnail_path'])
            
            # Step 3: Update database
            clip_id = self._save_to_database(context, final_video_path, thumbnail_success)
            
            # Step 4: Link to motion event
            self._link_to_motion_event(context, clip_id)
            
            logger.info(f"✅ Recording finalized for {camera_name}: {final_video_path}")
            
        except Exception as e:
            logger.error(f"❌ Failed to finalize recording for {camera_name}: {e}")
    
    def _merge_audio_video(self, context: Dict) -> Path:
        """Merge audio and video using ffmpeg if both exist"""
        video_path = context['video_path']
        audio_path = context['audio_path']
        
        if not context['has_audio'] or not audio_path or not audio_path.exists():
            # No audio to merge, return original video path
            return video_path
        
        try:
            # Create merged file path
            merged_path = video_path.with_suffix('.merged.mp4')
            
            # Use ffmpeg to merge audio and video
            cmd = [
                'ffmpeg', '-y',  # Overwrite output file
                '-i', str(video_path),  # Video input
                '-i', str(audio_path),  # Audio input
                '-c:v', 'copy',         # Copy video stream
                '-c:a', 'aac',          # Encode audio as AAC
                '-strict', 'experimental',
                str(merged_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                # Replace original video with merged version
                video_path.unlink()  # Remove original
                merged_path.rename(video_path)  # Rename merged to original name
                
                # Clean up audio file
                if audio_path.exists():
                    audio_path.unlink()
                
                logger.info(f"🎬 Audio/video merged successfully: {video_path}")
                context['has_audio'] = True
                
            else:
                logger.error(f"❌ ffmpeg merge failed: {result.stderr}")
                context['has_audio'] = False
                
        except Exception as e:
            logger.error(f"❌ Audio/video merge failed: {e}")
            context['has_audio'] = False
        
        return video_path
    
    def _generate_thumbnail(self, video_path: Path, thumbnail_path: Path) -> bool:
        """Generate thumbnail from video file"""
        if not OPENCV_AVAILABLE:
            logger.warning("🖼️ Thumbnail generation skipped (OpenCV not available)")
            return False
        
        try:
            # Use ffmpeg to extract frame at 2 seconds
            cmd = [
                'ffmpeg', '-y',  # Overwrite output
                '-i', str(video_path),
                '-ss', '2',      # Seek to 2 seconds
                '-vframes', '1', # Extract 1 frame
                '-q:v', '2',     # High quality
                str(thumbnail_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0 and thumbnail_path.exists():
                logger.info(f"🖼️ Thumbnail generated: {thumbnail_path}")
                return True
            else:
                logger.error(f"❌ Thumbnail generation failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Thumbnail generation failed: {e}")
            return False
    
    def _save_to_database(self, context: Dict, video_path: Path, has_thumbnail: bool) -> Optional[int]:
        """Save clip metadata to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            
            # Create relative paths for storage
            clips_base = Path('/home/p12146/Projects/Nutflix-platform/clips')
            rel_video_path = '/' + str(video_path.relative_to(clips_base.parent))
            rel_thumbnail_path = '/' + str(context['thumbnail_path'].relative_to(clips_base.parent)) if has_thumbnail else None
            
            # Insert clip metadata
            cur.execute('''
                INSERT INTO clip_metadata (
                    timestamp, camera, clip_path, thumbnail_path, duration, 
                    trigger_type, has_audio, species, behavior, confidence
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                context['start_time'].isoformat(),
                context['camera_name'],
                rel_video_path,
                rel_thumbnail_path,
                context['duration'],
                'pir_motion',
                context['has_audio'],
                'Wildlife',  # Default classification
                'investigating',  # Default behavior
                0.95  # High confidence for PIR detection
            ))
            
            clip_id = cur.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"📊 Clip metadata saved to database (ID: {clip_id})")
            return clip_id
            
        except Exception as e:
            logger.error(f"❌ Failed to save clip metadata: {e}")
            return None
    
    def _link_to_motion_event(self, context: Dict, clip_id: Optional[int]):
        """Link clip to corresponding motion event in database"""
        if not clip_id:
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            
            # Find the most recent motion event for this camera
            cur.execute('''
                SELECT id FROM motion_events 
                WHERE camera = ? AND motion_type = 'gpio'
                ORDER BY created_at DESC 
                LIMIT 1
            ''', (context['camera_name'],))
            
            result = cur.fetchone()
            if result:
                motion_event_id = result[0]
                
                # Update motion event with clip reference
                cur.execute('''
                    UPDATE motion_events 
                    SET clip_id = ?, duration = ?
                    WHERE id = ?
                ''', (clip_id, context['duration'], motion_event_id))
                
                conn.commit()
                logger.info(f"🔗 Linked clip {clip_id} to motion event {motion_event_id}")
            
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Failed to link clip to motion event: {e}")
    
    def get_recent_clips(self, camera_name: Optional[str] = None, limit: int = 10) -> list:
        """Get recent clips from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            
            if camera_name:
                cur.execute('''
                    SELECT * FROM clip_metadata 
                    WHERE camera = ? 
                    ORDER BY created_at DESC 
                    LIMIT ?
                ''', (camera_name, limit))
            else:
                cur.execute('''
                    SELECT * FROM clip_metadata 
                    ORDER BY created_at DESC 
                    LIMIT ?
                ''', (limit,))
            
            clips = cur.fetchall()
            conn.close()
            
            return clips
            
        except Exception as e:
            logger.error(f"❌ Failed to get recent clips: {e}")
            return []
    
    def stop_all_recordings(self):
        """Stop all active recordings"""
        with self.recording_lock:
            for camera_name, context in self.active_recordings.items():
                context['stop_event'].set()
                logger.info(f"🛑 Stopping recording for {camera_name}")
    
    def _create_placeholder_video(self, video_path: Path, duration: float):
        """Create a simple placeholder video file"""
        try:
            if OPENCV_AVAILABLE:
                # Create a simple black frame with text
                frame = np.zeros((480, 640, 3), dtype=np.uint8)
                
                # Add text
                font = cv2.FONT_HERSHEY_SIMPLEX
                text1 = f"PIR Recording"
                text2 = f"Duration: {duration:.1f}s"
                
                cv2.putText(frame, text1, (50, 200), font, 1, (255, 255, 255), 2)
                cv2.putText(frame, text2, (50, 250), font, 1, (255, 255, 255), 2)
                
                # Write video
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                video_writer = cv2.VideoWriter(str(video_path), fourcc, 1, (640, 480))
                
                # Write a few frames
                for _ in range(int(duration)):
                    video_writer.write(frame)
                
                video_writer.release()
                logger.info(f"📝 Created placeholder video: {video_path}")
            else:
                # Just create a text file if OpenCV not available
                video_path.write_text(f"PIR recording placeholder - Duration: {duration:.1f}s")
                
        except Exception as e:
            logger.error(f"❌ Failed to create placeholder video: {e}")

# Global instance
pir_recording_engine = PIRRecordingEngine()
