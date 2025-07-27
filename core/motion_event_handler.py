# motion_event_handler.py
"""
Nutflix Lite - Motion Event Handler

Bridges motion detection with video clip recording.
Handles motion events and triggers appropriate recording actions.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Callable
import threading
import time

from core.recording_engine import RecordingEngine
from core.clip_manager import ClipManager

logger = logging.getLogger(__name__)

class MotionEventHandler:
    """Handles motion detection events and triggers video recording"""
    
    def __init__(self, settings_manager=None):
        self.settings = settings_manager
        self.recording_engine = RecordingEngine(settings_manager)
        self.clip_manager = ClipManager(settings_manager)
        
        # Motion event tracking
        self.recent_motion_events = {}  # camera_id -> last_motion_time
        self.motion_cooldown = 5.0  # Minimum seconds between recordings per camera
        
        # Statistics
        self.stats = {
            'total_motion_events': 0,
            'recordings_triggered': 0,
            'recordings_skipped_cooldown': 0,
            'recordings_skipped_disabled': 0,
            'last_reset': datetime.now()
        }
        
        logger.info("🚨 MotionEventHandler initialized")
    
    def handle_motion_event(self, camera_name: str, timestamp: str, additional_data: Optional[Dict[str, Any]] = None) -> bool:
        """
        Handle a motion detection event
        
        Args:
            camera_name: Name of camera that detected motion
            timestamp: Timestamp string of the motion event
            additional_data: Optional additional motion data
            
        Returns:
            bool: True if recording was triggered
        """
        try:
            self.stats['total_motion_events'] += 1
            
            # Parse timestamp
            try:
                motion_time = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
            except:
                motion_time = datetime.now()
            
            logger.info(f"🚨 Motion detected on {camera_name} at {timestamp}")
            
            # Check if recording is enabled for this camera
            if not self._is_recording_enabled(camera_name):
                self.stats['recordings_skipped_disabled'] += 1
                logger.info(f"📹 Recording disabled for {camera_name}, skipping")
                return False
            
            # Check cooldown period
            if self._is_in_cooldown(camera_name, motion_time):
                self.stats['recordings_skipped_cooldown'] += 1
                logger.info(f"⏰ {camera_name} in cooldown period, skipping recording")
                return False
            
            # Update last motion time
            self.recent_motion_events[camera_name] = motion_time
            
            # Get recording settings
            clip_settings = self._get_clip_settings()
            duration = clip_settings.get('duration_seconds', 10.0)
            
            # Trigger recording
            success = self.recording_engine.start_recording(
                camera_id=camera_name,
                duration=duration,
                use_ir=None,  # Auto-detect based on lighting
                trigger_type='motion'
            )
            
            if success:
                self.stats['recordings_triggered'] += 1
                logger.info(f"🎬 Motion → Recording {duration}s clip on {camera_name}")
                
                # Schedule clip organization after recording completes
                threading.Timer(
                    duration + 2.0,  # Wait for recording to complete
                    self._organize_completed_clip,
                    args=(camera_name, motion_time)
                ).start()
                
                return True
            else:
                logger.warning(f"❌ Failed to start recording for {camera_name}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error handling motion event for {camera_name}: {e}")
            return False
    
    def _is_recording_enabled(self, camera_name: str) -> bool:
        """Check if recording is enabled for this camera"""
        try:
            clip_settings = self._get_clip_settings()
            
            # Check global enable
            if not clip_settings.get('enabled', True):
                return False
            
            # Check camera-specific enable
            record_on_motion = clip_settings.get('record_on_motion', {})
            camera_key = camera_name.lower()
            
            return record_on_motion.get(camera_key, True)
            
        except Exception as e:
            logger.error(f"❌ Error checking recording settings: {e}")
            return False
    
    def _is_in_cooldown(self, camera_name: str, motion_time: datetime) -> bool:
        """Check if camera is in cooldown period"""
        if camera_name not in self.recent_motion_events:
            return False
        
        last_motion = self.recent_motion_events[camera_name]
        time_diff = (motion_time - last_motion).total_seconds()
        
        return time_diff < self.motion_cooldown
    
    def _organize_completed_clip(self, camera_name: str, motion_time: datetime):
        """Organize the completed clip after recording finishes"""
        try:
            # This would typically find the most recent clip for this camera
            # and organize it using the clip manager
            logger.info(f"📁 Organizing completed clip for {camera_name}")
            
            # In a full implementation, you'd:
            # 1. Find the clip file that was just created
            # 2. Load its metadata
            # 3. Call clip_manager.organize_clip()
            
            # For now, just trigger cleanup if needed
            storage_stats = self.clip_manager.get_storage_stats()
            max_clips = self._get_clip_settings().get('max_clips', 100)
            
            if storage_stats.get('total_clips', 0) > max_clips:
                logger.info("🧹 Running clip cleanup after new recording")
                cleanup_stats = self.clip_manager.cleanup_old_clips()
                logger.info(f"🧹 Cleanup: {cleanup_stats}")
                
        except Exception as e:
            logger.error(f"❌ Error organizing clip for {camera_name}: {e}")
    
    def register_with_motion_detector(self, motion_detector):
        """Register this handler with a motion detector"""
        try:
            motion_detector.register_callback(self.handle_motion_event)
            logger.info("🔗 Registered with motion detector")
        except Exception as e:
            logger.error(f"❌ Failed to register with motion detector: {e}")
    
    def get_motion_statistics(self) -> Dict[str, Any]:
        """Get motion and recording statistics"""
        uptime = (datetime.now() - self.stats['last_reset']).total_seconds()
        
        return {
            'uptime_seconds': uptime,
            'total_motion_events': self.stats['total_motion_events'],
            'recordings_triggered': self.stats['recordings_triggered'],
            'recordings_skipped_cooldown': self.stats['recordings_skipped_cooldown'],
            'recordings_skipped_disabled': self.stats['recordings_skipped_disabled'],
            'success_rate': (
                self.stats['recordings_triggered'] / max(self.stats['total_motion_events'], 1) * 100
            ),
            'recent_motion_events': {
                camera: timestamp.isoformat()
                for camera, timestamp in self.recent_motion_events.items()
            },
            'active_recordings': self.recording_engine.get_active_recordings()
        }
    
    def reset_statistics(self):
        """Reset motion and recording statistics"""
        self.stats = {
            'total_motion_events': 0,
            'recordings_triggered': 0,
            'recordings_skipped_cooldown': 0,
            'recordings_skipped_disabled': 0,
            'last_reset': datetime.now()
        }
        logger.info("📊 Motion statistics reset")
    
    def set_motion_cooldown(self, cooldown_seconds: float):
        """Set the motion detection cooldown period"""
        self.motion_cooldown = cooldown_seconds
        logger.info(f"⏰ Motion cooldown set to {cooldown_seconds}s")
    
    def get_recent_clips(self, camera_name: Optional[str] = None, limit: int = 10) -> list:
        """Get recent clips, optionally filtered by camera"""
        try:
            clips = self.clip_manager.scan_clips(camera_id=camera_name, days_back=7)
            return clips[:limit]
        except Exception as e:
            logger.error(f"❌ Error getting recent clips: {e}")
            return []
    
    def _get_clip_settings(self) -> Dict[str, Any]:
        """Get clip recording settings"""
        if self.settings:
            try:
                return self.settings.get('clip_settings', {})
            except:
                pass
        
        return {
            'enabled': True,
            'duration_seconds': 10,
            'storage_path': './clips',
            'max_clips': 100,
            'enable_ir_at_night': True,
            'record_on_motion': {
                'nestcam': True,
                'crittercam': True
            }
        }

# Integration helper function
def create_motion_recording_system(settings_manager=None, motion_detector=None):
    """
    Convenience function to create and wire up the complete motion recording system
    
    Args:
        settings_manager: Optional settings manager instance
        motion_detector: Optional motion detector to register with
        
    Returns:
        MotionEventHandler instance
    """
    handler = MotionEventHandler(settings_manager)
    
    if motion_detector:
        handler.register_with_motion_detector(motion_detector)
    
    return handler
