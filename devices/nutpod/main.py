

import time
import os
import logging
import threading
from typing import Dict
from core.config.config_manager import get_config
from core.camera.camera_manager import CameraManager
from core.recording_engine import RecordingEngine  # Use the main recording engine
from core.stream.stream_server import StreamServer
from core.audio.audio_recorder import AudioRecorder
from core.sighting_service import SightingService  # For camera-based motion detection

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
    
    audio_recorder = None
    try:
        audio_recorder = AudioRecorder()
    except Exception as e:
        logging.warning(f"[Audio] AudioRecorder unavailable: {e}")
    
    stream_server = StreamServer("nutpod")
    stream_thread = threading.Thread(target=stream_server.run, kwargs={"host": "0.0.0.0", "port": 5000, "threaded": True}, daemon=True)
    stream_thread.start()
    print("[NutPod] Stream server started on port 5000.")

    # Initialize sighting service for camera-based motion detection
    sighting_service = SightingService(cam_mgr)
    sighting_service.start()
    logging.info("[Motion] Camera-based motion detection started via SightingService")

    # Motion callback to trigger video recording
    def handle_motion(sighting):
        """Handle motion detection from sighting service"""
        nonlocal last_mic_record_time
        
        camera_name = sighting.get('camera', 'Unknown')
        timestamp = sighting.get('timestamp', 'Unknown')
        
        logging.info(f"[Motion] Motion detected on {camera_name} at {timestamp}")
        
        # Start video recording
        try:
            success = recording_engine.start_recording(camera_name, duration=10.0, trigger_type="motion")
            if success:
                logging.info(f"[Motion] Started recording for {camera_name}")
            else:
                logging.warning(f"[Motion] Failed to start recording for {camera_name}")
        except Exception as e:
            logging.error(f"[Motion] Recording error: {e}")

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
                # Look for video clips with metadata
                clip_pattern = "clips/*.mp4"
                metadata_pattern = "clips/*.mp4.json"
                
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

    # Register motion callback with sighting service
    sighting_service.add_sighting_callback(handle_motion)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("[NutPod] Exiting cleanly.")
        sighting_service.stop()
        # Stop any active recordings
        active_recordings = recording_engine.get_active_recordings()
        for camera_id in active_recordings:
            recording_engine.stop_recording(camera_id)
        print("[NutPod] Stream server thread will exit with main process.")

if __name__ == "__main__":
    main()
