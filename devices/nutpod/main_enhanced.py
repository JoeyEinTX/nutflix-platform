#!/usr/bin/env python3
"""
NutPod Main Application - Enhanced with Modern Settings System

This version demonstrates how the new settings system integrates with existing
device code while providing enhanced privacy controls and type-safe configuration.

Key improvements:
- Type-safe settings access
- Built-in privacy controls
- Persistent configuration
- Backward compatibility with existing code
- Enhanced logging and error handling
"""

import time
import os
import logging
import threading
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import both old and new systems for comparison
from core.config.config_manager import get_config
from core.settings.integration import get_settings_integrator
from core.camera.camera_manager import CameraManager
from core.motion.motion_detector import MotionDetector
from core.recording.recording_engine import RecordingEngine
from core.stream.stream_server import StreamServer
from core.audio.audio_recorder import AudioRecorder

# Global variables for motion tracking
motion_flags = {}
last_mic_record_time = 0


def main():
    """Enhanced main function with settings system integration."""
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s',
        handlers=[
            logging.FileHandler("nutpod_motion_events.log"), 
            logging.StreamHandler()
        ]
    )
    
    print("🐿️ [NutPod Enhanced] Starting with modern settings system...")
    
    # Initialize settings integrator (provides both old and new config access)
    integrator = get_settings_integrator("nutpod")
    settings = integrator.settings
    
    # Migrate legacy config if needed
    if integrator.migrate_legacy_config():
        print("✅ [Settings] Legacy configuration migrated successfully")
    
    # Display current privacy status
    privacy_status = settings.get_privacy_status()
    print(f"🔒 [Privacy] Status: Recording={privacy_status['camera_recording']}, "
          f"Audio={privacy_status['audio_recording']}, "
          f"Streaming={privacy_status['camera_streaming']}")
    
    # Get configuration using both old and new methods for comparison
    print("\n📋 [Config] Comparison between old and new systems:")
    
    try:
        # Old system
        legacy_config = get_config("nutpod")
        print(f"   Legacy enabled cameras: {legacy_config.get('enabled_cameras', [])}")
    except Exception as e:
        print(f"   Legacy config not available: {e}")
    
    # New system - type-safe access
    print(f"   New primary camera: {settings.camera.primary_camera.name} "
          f"(enabled: {settings.camera.primary_camera.enabled})")
    print(f"   New secondary camera: {settings.camera.secondary_camera.name} "
          f"(enabled: {settings.camera.secondary_camera.enabled})")
    print(f"   Motion sensitivity: {settings.motion.detection.sensitivity}")
    print(f"   Audio recording: {settings.audio.recording.enabled}")
    print(f"   Data retention: {settings.privacy.data.retention_period} days")
    
    # Check if recording/streaming is allowed based on privacy settings
    if not settings.is_recording_allowed():
        print("⚠️  [Privacy] Recording is disabled by privacy settings!")
        print("   To enable recording, check privacy.camera.recording_enabled")
        
    if not settings.is_streaming_allowed():
        print("⚠️  [Privacy] Streaming is disabled by privacy settings!")
    
    # Initialize core components with privacy-aware settings
    print("\n🎬 [Components] Initializing core components...")
    
    # Camera Manager
    cam_mgr = CameraManager("nutpod")
    
    # Recording Engine - only initialize if recording is allowed
    recorder = None
    if settings.is_recording_allowed():
        recorder = RecordingEngine("nutpod", cam_mgr)
        print("✅ [Recording] Recording engine initialized")
    else:
        print("🔒 [Recording] Recording engine disabled by privacy settings")
    
    # Audio Recorder - privacy-aware initialization
    audio_recorder = None
    if settings.is_audio_recording_allowed():
        try:
            audio_recorder = AudioRecorder()
            print("✅ [Audio] Audio recorder initialized")
        except Exception as e:
            logging.warning(f"[Audio] AudioRecorder unavailable: {e}")
    else:
        print("🔒 [Audio] Audio recording disabled by privacy settings")
    
    # Stream Server - privacy-aware initialization
    stream_server = None
    stream_thread = None
    if settings.is_streaming_allowed():
        stream_server = StreamServer("nutpod")
        stream_port = settings.network.streaming_port
        stream_thread = threading.Thread(
            target=stream_server.run, 
            kwargs={"host": "0.0.0.0", "port": stream_port, "threaded": True}, 
            daemon=True
        )
        stream_thread.start()
        print(f"✅ [Streaming] Stream server started on port {stream_port}")
    else:
        print("🔒 [Streaming] Streaming disabled by privacy settings")
    
    # Motion Detection Setup
    print("\n🎯 [Motion] Setting up motion detection...")
    
    # Get motion configuration from new settings system
    motion_config = integrator.get_motion_config()
    motion_sensor_pins = motion_config['motion_sensors']
    cooldown_sec = motion_config['cooldown_period']
    sensitivity = motion_config['motion_sensitivity']
    
    print(f"   Motion sensors: {motion_sensor_pins}")
    print(f"   Sensitivity: {sensitivity}")
    print(f"   Cooldown: {cooldown_sec}s")
    
    # Initialize motion tracking
    global motion_flags
    last_trigger = {cam: 0 for cam in motion_sensor_pins}
    for cam in motion_sensor_pins:
        motion_flags[cam] = 0
    
    def handle_motion(camera_name, timestamp):
        """Enhanced motion handler with privacy controls."""
        global last_mic_record_time
        
        now = time.time()
        
        # Check cooldown
        if now - last_trigger[camera_name] < cooldown_sec:
            logging.info(f"[Motion] {camera_name} trigger ignored (cooldown)")
            return
            
        last_trigger[camera_name] = now
        motion_flags[camera_name] = now
        logging.info(f"[Motion] Motion detected on {camera_name} at {timestamp}")
        
        # Start recording only if privacy allows and recorder is available
        if recorder and settings.is_recording_allowed():
            if not recorder.is_recording():
                logging.info(f"[Motion] Starting recording for {camera_name}")
                recorder.start_recording(camera_name)
            else:
                logging.info(f"[Motion] Already recording; skipping new trigger for {camera_name}")
        elif not settings.is_recording_allowed():
            logging.info(f"[Motion] Recording disabled by privacy settings for {camera_name}")
        
        # Motion-triggered audio with enhanced privacy controls
        if camera_name == "NestCam" and settings.is_audio_recording_allowed():
            if audio_recorder is not None:
                # Get audio settings from new system
                audio_config = integrator.get_audio_config()
                mic_cooldown = 30  # Could be moved to settings
                mic_duration = audio_config['duration']
                
                if now - last_mic_record_time > mic_cooldown:
                    def record_audio():
                        ts = time.strftime('%Y%m%d_%H%M%S')
                        # Use storage path from settings
                        storage_config = integrator.get_storage_config()
                        recordings_dir = Path(storage_config['base_path']) / storage_config['recordings_path']
                        recordings_dir.mkdir(parents=True, exist_ok=True)
                        
                        fname = recordings_dir / f"audio_{camera_name}_{ts}.{audio_config['audio_format']}"
                        
                        try:
                            logging.info(f"[Audio] Starting mic recording for {camera_name} ({mic_duration}s)")
                            audio_recorder.start_recording(str(fname))
                            time.sleep(mic_duration)
                            audio_recorder.stop_recording()
                            logging.info(f"[Audio] Saved mic recording: {fname}")
                        except Exception as e:
                            logging.warning(f"[Audio] Mic recording failed: {e}")
                    
                    threading.Thread(target=record_audio, daemon=True).start()
                    last_mic_record_time = now
                else:
                    logging.info(f"[Audio] Mic recording cooldown active for {camera_name}")
            else:
                logging.warning(f"[Audio] AudioRecorder not available; skipping mic recording for {camera_name}")
        elif camera_name == "NestCam" and not settings.is_audio_recording_allowed():
            logging.info(f"[Audio] Mic recording disabled by privacy settings for {camera_name}")
    
    # Initialize Motion Detector
    if motion_sensor_pins:
        motion = MotionDetector(
            motion_sensor_pins, 
            callback=handle_motion, 
            debounce_sec=settings.motion.sensors.debounce_time
        )
        motion.start()
        print("✅ [Motion] Motion detector started")
    else:
        motion = None
        print("⚠️  [Motion] No motion sensors configured")
    
    # Display runtime information
    print(f"\n🚀 [Runtime] NutPod Enhanced is running!")
    print(f"   Device: {settings.system.device_name}")
    print(f"   Location: {settings.system.device_location or 'Not set'}")
    print(f"   Timezone: {settings.system.timezone}")
    print(f"   Settings file: {settings.config_path}")
    print("   Press Ctrl+C to stop")
    
    # Main loop
    try:
        loop_count = 0
        while True:
            time.sleep(1)
            loop_count += 1
            
            # Every 60 seconds, show status and check for settings changes
            if loop_count % 60 == 0:
                active_motion = [cam for cam, flag in motion_flags.items() 
                               if flag > 0 and (time.time() - flag) < 30]
                if active_motion:
                    print(f"📊 [Status] Recent motion: {active_motion}")
                
                # Check if privacy settings have changed
                current_privacy = settings.get_privacy_status()
                if not current_privacy['camera_recording'] and recorder:
                    print("🔒 [Privacy] Recording was disabled - stopping active recording")
                    if recorder.is_recording():
                        recorder.stop_recording()
                        
    except KeyboardInterrupt:
        print("\n🛑 [NutPod Enhanced] Exiting cleanly...")
        
        # Clean shutdown
        if motion:
            motion.stop()
            print("✅ [Motion] Motion detector stopped")
            
        if recorder and recorder.is_recording():
            recorder.stop_recording()
            print("✅ [Recording] Recording stopped")
            
        if stream_thread:
            print("✅ [Streaming] Stream server thread will exit with main process")
        
        # Save current settings state
        try:
            settings.save()
            print("✅ [Settings] Configuration saved")
        except Exception as e:
            logging.warning(f"[Settings] Could not save configuration: {e}")
        
        print("🐿️ [NutPod Enhanced] Shutdown complete")


def test_settings_functionality():
    """Test function to demonstrate settings system features."""
    print("\n🧪 [Test] Settings System Functionality Test")
    print("=" * 50)
    
    # Get settings integrator
    integrator = get_settings_integrator("nutpod")
    settings = integrator.settings
    
    print("\n1. Privacy Controls Test:")
    print(f"   Current privacy status: {settings.get_privacy_status()}")
    
    print("\n2. Settings Modification Test:")
    original_sensitivity = settings.motion.detection.sensitivity
    print(f"   Original motion sensitivity: {original_sensitivity}")
    
    # Temporarily modify
    settings.motion.detection.sensitivity = 0.8
    print(f"   Modified motion sensitivity: {settings.motion.detection.sensitivity}")
    
    # Restore original
    settings.motion.detection.sensitivity = original_sensitivity
    print(f"   Restored motion sensitivity: {settings.motion.detection.sensitivity}")
    
    print("\n3. Configuration Compatibility Test:")
    try:
        compatible_config = integrator.get_compatible_config()
        print(f"   Compatible config keys: {list(compatible_config.keys())}")
        print(f"   Enabled cameras: {compatible_config.get('enabled_cameras', [])}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n4. Privacy Mode Test:")
    print(f"   Recording allowed before privacy mode: {settings.is_recording_allowed()}")
    settings.enable_privacy_mode()
    print(f"   Recording allowed during privacy mode: {settings.is_recording_allowed()}")
    settings.disable_privacy_mode()
    print(f"   Recording allowed after privacy mode: {settings.is_recording_allowed()}")
    
    print("\n✅ [Test] Settings functionality test complete!")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_settings_functionality()
    else:
        main()
