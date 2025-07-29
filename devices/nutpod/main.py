

import sys
import os
from pathlib import Path

# Add the project root to Python path so we can import 'core'
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import time
import logging
import threading
from typing import Dict
from core.config.config_manager import get_config
from core.camera.camera_manager import CameraManager
from core.recording_engine import RecordingEngine  
# TEMPORARILY DISABLED: from core.audio.audio_recorder import AudioRecorder
from core.sighting_service import SightingService  
from core.motion.dual_pir_motion_detector import DualPIRMotionDetector  # New PIR motion detection
from utils.env_sensor import EnvSensor  # BME280 environmental sensor

def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s',
        handlers=[logging.FileHandler("motion_events.log"), logging.StreamHandler()]
    )
    print("[NutPod] Starting test harness with stream server...")

    # Global privacy toggle for mic recording
    ENABLE_MIC_RECORDING = True  # Set False to disable all audio capture
    MIC_RECORDING_COOLDOWN = 30  # seconds
    MIC_RECORDING_DURATION = 10  # seconds
    last_mic_record_time = 0

    config = get_config("nutpod")
    cam_mgr = CameraManager("nutpod")
    
    # Use the main RecordingEngine instead of the old one
    recording_engine = RecordingEngine()
    
    # Initialize environmental sensor (BME280)
    env_sensor = EnvSensor()
    logging.info("[EnvSensor] BME280 environmental sensor initialized")
    
    # TEMPORARILY DISABLED: Audio recording while focusing on PIR motion detection
    audio_recorder = None
    # try:
    #     audio_recorder = AudioRecorder()
    # except Exception as e:
    #     logging.warning(f"[Audio] AudioRecorder unavailable: {e}")
    logging.info("[Audio] Audio recording temporarily disabled - focusing on PIR motion detection")
    
    # NOTE: StreamServer removed - using dashboard's integrated streaming instead
    # This eliminates camera hardware conflicts and reduces resource usage
    print("[NutPod] Using dashboard's on-demand streaming (port 8000)")

    # Initialize PIR motion detection (replaces camera-based motion detection)
    def handle_pir_motion(camera_name, motion_event):
        """Handle motion detection from PIR sensors"""
        nonlocal last_mic_record_time
        
        timestamp = motion_event.get('timestamp', 'Unknown')
        gpio_pin = motion_event.get('gpio_pin', 'Unknown')
        
        print(f"[NutPod PIRHandler] 🚨 PIR motion detected for {camera_name} (GPIO {gpio_pin})")
        logging.info(f"[PIR Motion] Motion detected on {camera_name} at {timestamp}")
        
        # Save motion event to database (FIX: This was missing!)
        try:
            motion_data = {
                'camera': camera_name,
                'type': 'gpio',  # PIR sensor type
                'confidence': 0.9,  # PIR sensors are highly reliable
                'duration': 3.0,  # Typical PIR pulse duration
                'gpio_pin': gpio_pin,
                'sensor_type': motion_event.get('sensor_type', 'PIR')
            }
            sighting_service._record_motion_event(timestamp, motion_data)
            logging.info(f"[PIR Motion] Saved motion event to database for {camera_name}")
        except Exception as e:
            logging.error(f"[PIR Motion] Database save error: {e}")
        
        # Start video recording
        try:
            success = recording_engine.start_recording(camera_name, duration=10.0, trigger_type="pir_motion")
            if success:
                logging.info(f"[PIR Motion] Started recording for {camera_name}")
            else:
                logging.warning(f"[PIR Motion] Failed to start recording for {camera_name}")
        except Exception as e:
            logging.error(f"[PIR Motion] Recording error: {e}")

        # Motion-triggered audio for NestCam
        if camera_name == "NestCam" and ENABLE_MIC_RECORDING:
            if audio_recorder is not None:
                now = time.time()
                if now - last_mic_record_time > MIC_RECORDING_COOLDOWN:
                    def record_audio():
                        ts = time.strftime('%Y%m%d_%H%M%S')
                        fname = f"recordings/audio_{camera_name}_{ts}.wav"
                        try:
                            logging.info(f"[Audio] Starting mic recording for {camera_name} ({MIC_RECORDING_DURATION}s)")
                            audio_recorder.start_recording(fname)
                            time.sleep(MIC_RECORDING_DURATION)
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
        elif camera_name == "NestCam" and not ENABLE_MIC_RECORDING:
            logging.info(f"[Audio] Mic recording disabled by privacy flag; skipping for {camera_name}")

    # Initialize dual PIR motion detector
    pir_detector = DualPIRMotionDetector(motion_callback=handle_pir_motion)
    pir_detector.start_detection()
    logging.info("[PIR Motion] Dual PIR motion detection started for CritterCam (GPIO 18) and NestCam (GPIO 24)")

    # Keep sighting service for creating sightings from recordings, but disable camera motion detection
    sighting_service = SightingService()
    sighting_service.camera_manager = cam_mgr  # Set camera manager manually
    # NOTE: Not starting sighting_service.start() to avoid camera conflicts
    
    # Environmental monitoring function
    def monitor_environment():
        """Periodically log environmental data from BME280"""
        while True:
            try:
                env_data = env_sensor.read()
                logging.info(f"[Environment] Temp: {env_data['temperature']}°C, "
                           f"Humidity: {env_data['humidity']}%, "
                           f"Pressure: {env_data['pressure']} hPa")
                time.sleep(300)  # Log every 5 minutes
            except Exception as e:
                logging.error(f"[Environment] Error reading BME280: {e}")
                time.sleep(60)  # Retry in 1 minute on error
    
    # Start environmental monitoring in background
    env_thread = threading.Thread(target=monitor_environment, daemon=True)
    env_thread.start()
    logging.info("[Environment] BME280 monitoring started (5-minute intervals)")
    
    # Recording completion callback to create sightings from recorded clips
    def handle_recording_complete(camera_name: str, recording_metadata: Dict):
        """Handle completed video recording and create sighting"""
        try:
            logging.info(f"[Recording] Recording completed for {camera_name}: {recording_metadata.get('filename', 'unknown')}")
            
            # Create sighting from the recording
            sighting = sighting_service.create_sighting_from_recording(camera_name, recording_metadata)
            if sighting:
                logging.info(f"[Sighting] Created sighting from recording: {sighting.get('species', 'Unknown')}")
            else:
                logging.warning(f"[Sighting] Failed to create sighting from recording")
                
        except Exception as e:
            logging.error(f"[Recording] Error handling recording completion: {e}")
    
    # Register recording completion callback (if supported by recording engine)
    # For now, we'll poll for new recordings periodically
    
    # Monitor for completed recordings and create sightings
    def monitor_recordings():
        """Monitor for completed recordings and create sightings"""
        import json
        import glob
        
        processed_clips = set()
        
        while True:
            try:
                # Look for video clips with metadata (FIX: Changed from .mp4 to .h264)
                clip_pattern = "clips/*.h264"
                metadata_pattern = "clips/*.h264.json"
                
                metadata_files = glob.glob(metadata_pattern)
                
                for metadata_file in metadata_files:
                    if metadata_file not in processed_clips:
                        try:
                            with open(metadata_file, 'r') as f:
                                recording_metadata = json.load(f)
                            
                            camera_name = recording_metadata.get('camera_id', 'Unknown')
                            handle_recording_complete(camera_name, recording_metadata)
                            
                            processed_clips.add(metadata_file)
                            
                        except Exception as e:
                            logging.error(f"[Monitor] Error processing metadata {metadata_file}: {e}")
                
                # Clean up processed clips set to prevent memory growth
                if len(processed_clips) > 1000:
                    processed_clips = set(list(processed_clips)[-500:])
                
                time.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                logging.error(f"[Monitor] Recording monitor error: {e}")
                time.sleep(10)
    
    # Start recording monitor thread
    monitor_thread = threading.Thread(target=monitor_recordings, daemon=True)
    monitor_thread.start()
    logging.info("[Monitor] Recording monitor started")

    # PIR motion detection is now handling motion events directly
    # No need to register camera-based motion callbacks
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("[NutPod] Exiting cleanly.")
        pir_detector.stop_detection()  # Stop PIR detection
        # Stop any active recordings
        active_recordings = recording_engine.get_active_recordings()
        for camera_id in active_recordings:
            recording_engine.stop_recording(camera_id)
        print("[NutPod] PIR motion detection stopped.")

if __name__ == "__main__":
    main()
