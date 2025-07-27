# recording_engine.py
"""
Nutflix Lite - Event-Based Video Clip Recording Engine

Handles short video clip recording triggered by motion detection.
Integrates with IR LED control for low-light recording.
Uses Picamera2 for H.264 recording with automatic conversion to MP4.
"""

import os
import time
import threading
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import subprocess

try:
    from picamera2 import Picamera2
    from picamera2.encoders import H264Encoder
    from picamera2.outputs import FileOutput
    PICAMERA2_AVAILABLE = True
except ImportError:
    PICAMERA2_AVAILABLE = False

from core.infrared.smart_ir_controller import SmartIRController
from core.camera.camera_manager import CameraManager

logger = logging.getLogger(__name__)

class RecordingEngine:
    """Coordinates motion-triggered video clip recording with IR LED support"""
    
    def __init__(self, settings_manager=None):
        self.settings = settings_manager
        try:
            self.camera_manager = CameraManager('nutpod')  # Default device name
        except Exception as e:
            logger.warning(f"⚠️ CameraManager initialization failed: {e}, using mock")
            self.camera_manager = None
        
        self.ir_controller = SmartIRController()
        
        # Active recordings tracker
        self.active_recordings: Dict[str, Dict[str, Any]] = {}
        self._recording_lock = threading.Lock()
        
        logger.info("🎬 RecordingEngine initialized")
    
    def start_recording(self, camera_id: str, duration: float = 10.0, use_ir: bool = None, trigger_type: str = "motion") -> bool:
        """
        Start recording a video clip
        
        Args:
            camera_id: Camera identifier ('NestCam' or 'CritterCam')
            duration: Recording duration in seconds
            use_ir: Force IR LED state (None = auto-detect)
            trigger_type: What triggered the recording ('motion', 'manual', etc.)
            
        Returns:
            bool: True if recording started successfully
        """
        with self._recording_lock:
            # Check if this camera is already recording
            if camera_id in self.active_recordings:
                logger.warning(f"📹 {camera_id} is already recording, skipping new request")
                return False
            
            try:
                # Get camera settings from settings manager
                clip_settings = self._get_clip_settings()
                if not clip_settings.get('enabled', True):
                    logger.info(f"📹 Clip recording disabled for {camera_id}")
                    return False
                
                # Check if recording is enabled for this specific camera
                record_on_motion = clip_settings.get('record_on_motion', {})
                if not record_on_motion.get(camera_id.lower(), True):
                    logger.info(f"📹 Motion recording disabled for {camera_id}")
                    return False
                
                # Determine IR LED usage
                if use_ir is None:
                    use_ir = self.ir_controller.should_use_ir(camera_id)
                
                # Create recording context
                recording_context = {
                    'camera_id': camera_id,
                    'start_time': datetime.now(),
                    'duration': duration,
                    'use_ir': use_ir,
                    'trigger_type': trigger_type,
                    'thread': None,
                    'ir_active': False
                }
                
                # Start recording thread
                recording_thread = threading.Thread(
                    target=self._record_clip_thread,
                    args=(recording_context,),
                    daemon=True
                )
                recording_context['thread'] = recording_thread
                self.active_recordings[camera_id] = recording_context
                
                recording_thread.start()
                
                logger.info(f"🎬 Started {duration}s clip recording on {camera_id} (IR: {use_ir}, trigger: {trigger_type})")
                return True
                
            except Exception as e:
                logger.error(f"❌ Failed to start recording on {camera_id}: {e}")
                return False
    
    def _record_clip_thread(self, context: Dict[str, Any]):
        """Recording thread that handles the actual video capture"""
        camera_id = context['camera_id']
        
        try:
            # Activate IR LED if needed
            if context['use_ir']:
                self.ir_controller.activate_for_camera(camera_id)
                context['ir_active'] = True
                logger.info(f"🔦 IR LED activated for {camera_id}")
            
            # Generate filename
            filename = self._generate_filename(context)
            
            if PICAMERA2_AVAILABLE:
                success = self._record_with_picamera2(camera_id, filename, context['duration'])
            else:
                success = self._record_mock_clip(filename, context)
            
            if success:
                # Convert H.264 to MP4 if needed
                mp4_filename = self._convert_to_mp4(filename)
                logger.info(f"✅ Clip recorded: {mp4_filename}")
                
                # Create thumbnail from the recorded video
                try:
                    from core.utils.video_thumbnail_extractor import video_thumbnail_extractor
                    thumbnail_path = video_thumbnail_extractor.extract_thumbnail_from_video(
                        mp4_filename, 
                        context['start_time'].isoformat(), 
                        camera_id
                    )
                    if thumbnail_path:
                        logger.info(f"📸 Thumbnail created: {thumbnail_path}")
                    else:
                        logger.warning(f"⚠️ Failed to create thumbnail for {mp4_filename}")
                except Exception as e:
                    logger.error(f"❌ Thumbnail creation failed: {e}")
                    thumbnail_path = None
                
                # Store metadata with thumbnail path
                metadata = {
                    'camera_id': camera_id,
                    'start_time': context['start_time'].isoformat(),
                    'duration': context['duration'],
                    'trigger_type': context['trigger_type'],
                    'ir_used': context['use_ir'],
                    'filename': mp4_filename,
                    'thumbnail_path': thumbnail_path
                }
                self._save_metadata(mp4_filename, metadata)
            else:
                logger.error(f"❌ Failed to record clip for {camera_id}")
        
        except Exception as e:
            logger.error(f"❌ Recording thread error for {camera_id}: {e}")
        
        finally:
            # Cleanup
            if context['ir_active']:
                self.ir_controller.deactivate()
                logger.info(f"🔦 IR LED deactivated for {camera_id}")
            
            # Remove from active recordings
            with self._recording_lock:
                if camera_id in self.active_recordings:
                    del self.active_recordings[camera_id]
    
    def _record_with_picamera2(self, camera_id: str, filename: str, duration: float) -> bool:
        """Record using Picamera2"""
        try:
            # Check if camera manager is available
            if not self.camera_manager:
                logger.warning(f"❌ CameraManager not available, falling back to mock")
                return self._record_mock_clip(filename, {'camera_id': camera_id, 'duration': duration, 'trigger_type': 'mock', 'use_ir': False, 'start_time': datetime.now()})
            
            # Get camera instance
            camera = self.camera_manager.get_camera(camera_id)
            if not camera:
                logger.error(f"❌ Camera {camera_id} not available")
                return False
            
            # Configure for video recording
            video_config = camera.create_video_configuration()
            camera.configure(video_config)
            
            # Create encoder and output
            encoder = H264Encoder(bitrate=10000000)  # 10 Mbps
            output = FileOutput(filename)
            
            # Start recording
            camera.start_recording(encoder, output)
            logger.info(f"🎥 Recording {camera_id} to {filename} for {duration}s")
            
            # Record for specified duration
            time.sleep(duration)
            
            # Stop recording
            camera.stop_recording()
            logger.info(f"⏹️ Stopped recording {camera_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Picamera2 recording error: {e}")
            return False
    
    def _record_mock_clip(self, filename: str, context: Dict[str, Any]) -> bool:
        """Create a mock video file for development"""
        try:
            # Create a simple text file as a mock clip
            mock_content = f"""Mock Video Clip
Camera: {context['camera_id']}
Start Time: {context['start_time']}
Duration: {context['duration']}s
Trigger: {context['trigger_type']}
IR Used: {context['use_ir']}
"""
            with open(filename + ".mock", 'w') as f:
                f.write(mock_content)
            
            time.sleep(min(context['duration'], 2.0))  # Simulate recording time
            logger.info(f"🎭 Mock clip created: {filename}.mock")
            return True
            
        except Exception as e:
            logger.error(f"❌ Mock recording error: {e}")
            return False
    
    def _generate_filename(self, context: Dict[str, Any]) -> str:
        """Generate filename for the clip"""
        timestamp = context['start_time'].strftime("%Y%m%d_%H%M%S")
        camera_short = context['camera_id'][:4].lower()  # nest, crit
        trigger_short = context['trigger_type'][:3].lower()  # mot, man
        ir_suffix = "_ir" if context['use_ir'] else ""
        
        clip_settings = self._get_clip_settings()
        storage_path = Path(clip_settings.get('storage_path', './clips'))
        storage_path.mkdir(parents=True, exist_ok=True)
        
        filename = f"{camera_short}_{timestamp}_{trigger_short}{ir_suffix}.h264"
        return str(storage_path / filename)
    
    def _convert_to_mp4(self, h264_filename: str) -> str:
        """Convert H.264 file to MP4 using ffmpeg"""
        mp4_filename = h264_filename.replace('.h264', '.mp4')
        
        try:
            if h264_filename.endswith('.mock'):
                # Just rename mock file
                os.rename(h264_filename, mp4_filename.replace('.mp4', '.mock'))
                return mp4_filename.replace('.mp4', '.mock')
            
            # Use ffmpeg to convert
            cmd = [
                'ffmpeg', '-i', h264_filename, 
                '-c', 'copy', '-y',  # Copy stream, overwrite output
                mp4_filename
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                # Remove original H.264 file
                os.remove(h264_filename)
                return mp4_filename
            else:
                logger.warning(f"⚠️ ffmpeg conversion failed, keeping H.264: {result.stderr}")
                return h264_filename
                
        except Exception as e:
            logger.warning(f"⚠️ MP4 conversion failed: {e}, keeping H.264")
            return h264_filename
    
    def _save_metadata(self, video_filename: str, metadata: Dict[str, Any]):
        """Save clip metadata as JSON"""
        import json
        
        metadata_filename = video_filename + ".json"
        try:
            with open(metadata_filename, 'w') as f:
                json.dump(metadata, f, indent=2)
            logger.info(f"💾 Metadata saved: {metadata_filename}")
        except Exception as e:
            logger.error(f"❌ Failed to save metadata: {e}")
    
    def _get_clip_settings(self) -> Dict[str, Any]:
        """Get clip recording settings from settings manager or defaults"""
        if self.settings:
            try:
                return self.settings.get('clip_settings', {})
            except:
                pass
        
        # Default settings
        return {
            'enabled': True,
            'duration_seconds': 10,
            'storage_path': './clips',
            'max_clips': 100,
            'enable_ir_at_night': True,
            'ir_gpio_pin': 23,
            'record_on_motion': {
                'nestcam': True,
                'crittercam': True
            }
        }
    
    def get_active_recordings(self) -> Dict[str, Dict[str, Any]]:
        """Get currently active recordings"""
        with self._recording_lock:
            return {k: {
                'camera_id': v['camera_id'],
                'start_time': v['start_time'].isoformat(),
                'duration': v['duration'],
                'elapsed': (datetime.now() - v['start_time']).total_seconds(),
                'use_ir': v['use_ir'],
                'trigger_type': v['trigger_type']
            } for k, v in self.active_recordings.items()}
    
    def stop_recording(self, camera_id: str) -> bool:
        """Manually stop an active recording"""
        with self._recording_lock:
            if camera_id in self.active_recordings:
                # Note: In a full implementation, you'd need to signal the recording thread to stop
                logger.info(f"⏹️ Stop requested for {camera_id}")
                return True
            return False
