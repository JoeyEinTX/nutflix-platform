
import time

from core.config.config_manager import get_config
from core.camera.camera_manager import CameraManager
from core.motion.motion_detector import MotionDetector
from core.recording.recording_engine import RecordingEngine
from core.stream.stream_server import StreamServer
import threading

def main():
    print("[NutPod] Starting test harness with stream server...")
    config = get_config("nutpod")
    cam_mgr = CameraManager("nutpod")
    motion = MotionDetector(motion_sensitivity=config.get("motion_sensitivity", 0.4))
    recorder = RecordingEngine("nutpod", cam_mgr)
    stream_server = StreamServer("nutpod")
    stream_thread = threading.Thread(target=stream_server.run, kwargs={"host": "0.0.0.0", "port": 5000, "threaded": True}, daemon=True)
    stream_thread.start()
    print("[NutPod] Stream server started on port 5000.")
    cam_name = "CritterCam"
    no_motion_secs = 0
    stop_after = 3  # seconds with no motion before stopping recording
    try:
        while True:
            frame = cam_mgr.get_frame(cam_name)
            detected = motion.detect_motion(frame)
            if detected:
                print("[NutPod] Motion detected!")
                no_motion_secs = 0
                if not recorder.is_recording():
                    print("[NutPod] Starting recording...")
                    recorder.start_recording("motion")
            else:
                if recorder.is_recording():
                    no_motion_secs += 0.2
                    if no_motion_secs > stop_after:
                        print("[NutPod] No motion, stopping recording.")
                        recorder.stop_recording()
            time.sleep(0.2)
    except KeyboardInterrupt:
        print("[NutPod] Exiting cleanly.")
        if recorder.is_recording():
            recorder.stop_recording()
        # Flask's built-in server does not support programmatic shutdown, but if using gunicorn or waitress, add shutdown logic here.
        print("[NutPod] Stream server thread will exit with main process.")
