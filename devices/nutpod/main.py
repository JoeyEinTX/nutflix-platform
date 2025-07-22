

import time
import os
import logging
import threading
from core.config.config_manager import get_config
from core.camera.camera_manager import CameraManager
from core.motion.motion_detector import MotionDetector
from core.recording.recording_engine import RecordingEngine
from core.stream.stream_server import StreamServer
from core.audio.audio_recorder import AudioRecorder

def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s',
        handlers=[logging.FileHandler("motion_events.log"), logging.StreamHandler()]
    print("[NutPod] Starting test harness with stream server...")

# Global privacy toggle for mic recording
ENABLE_MIC_RECORDING = True  # Set False to disable all audio capture
MIC_RECORDING_COOLDOWN = 30  # seconds
MIC_RECORDING_DURATION = 10  # seconds
last_mic_record_time = 0

    config = get_config("nutpod")
    cam_mgr = CameraManager("nutpod")
    recorder = RecordingEngine("nutpod", cam_mgr)
    audio_recorder = None
    try:
        audio_recorder = AudioRecorder()
    except Exception as e:
        logging.warning(f"[Audio] AudioRecorder unavailable: {e}")
    stream_server = StreamServer("nutpod")
    stream_thread = threading.Thread(target=stream_server.run, kwargs={"host": "0.0.0.0", "port": 5000, "threaded": True}, daemon=True)
    stream_thread.start()
    print("[NutPod] Stream server started on port 5000.")

    # MotionDetector integration
    # Example GPIO pins; in production, load from config or environment
    motion_sensor_pins = config.get("motion_sensors", {"CritterCam": 17, "NestCam": 27})
    cooldown_sec = 10
    global motion_flags
    last_trigger = {cam: 0 for cam in motion_sensor_pins}
    for cam in motion_sensor_pins:
        motion_flags[cam] = 0

    def handle_motion(camera_name, timestamp):
        now = time.time()
        if now - last_trigger[camera_name] < cooldown_sec:
            logging.info(f"[Motion] {camera_name} trigger ignored (cooldown)")
            return
        last_trigger[camera_name] = now
        motion_flags[camera_name] = now
        logging.info(f"[Motion] Motion detected on {camera_name} at {timestamp}")
        if not recorder.is_recording():
            logging.info(f"[Motion] Starting recording for {camera_name}")
            recorder.start_recording(camera_name)
        else:
            logging.info(f"[Motion] Already recording; skipping new trigger for {camera_name}")

        # Motion-triggered audio for NestCam
        global last_mic_record_time
        if camera_name == "NestCam" and ENABLE_MIC_RECORDING:
            if audio_recorder is not None:
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

    motion = MotionDetector(motion_sensor_pins, callback=handle_motion, debounce_sec=2.0)
    motion.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("[NutPod] Exiting cleanly.")
        motion.stop()
        if recorder.is_recording():
            recorder.stop_recording()
        print("[NutPod] Stream server thread will exit with main process.")
