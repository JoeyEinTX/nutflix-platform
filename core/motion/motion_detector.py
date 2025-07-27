import threading
import time
import logging
import sys

try:
    import RPi.GPIO as GPIO
    ON_PI = True
except ImportError:
    ON_PI = False

class MotionDetector:
    def __init__(self, sensor_config, callback=None, debounce_sec=2.0):
        """
        sensor_config: dict mapping camera name to GPIO pin
        callback: function(camera_name, timestamp)
        debounce_sec: cooldown per camera
        """
        self.sensor_config = sensor_config
        self.callback = callback
        self.debounce_sec = debounce_sec
        self._threads = []
        self._stop_event = threading.Event()
        self._last_trigger = {cam: 0 for cam in sensor_config}
        self.motion_history = []  # List of recent motion events (dicts)
        if ON_PI:
            GPIO.setmode(GPIO.BCM)
            for pin in sensor_config.values():
                GPIO.setup(pin, GPIO.IN)
        logging.info(f"MotionDetector initialized for: {sensor_config}")

    def _watch_sensor(self, camera_name, pin):
        logging.info(f"Watcher started for {camera_name} (GPIO {pin})")
        while not self._stop_event.is_set():
            triggered = False
            if ON_PI:
                if GPIO.input(pin):
                    triggered = True
            else:
                # Simulate trigger every 10s in dev
                if int(time.time()) % 10 == 0:
                    triggered = True
            now = time.time()
            if triggered and (now - self._last_trigger[camera_name] > self.debounce_sec):
                self._last_trigger[camera_name] = now
                ts = time.strftime('%Y-%m-%d %H:%M:%S')
                event = {"timestamp": ts, "camera": camera_name, "trigger": "Motion"}
                self.motion_history.append(event)
                if len(self.motion_history) > 20:
                    self.motion_history = self.motion_history[-20:]
                logging.info(f"Motion detected on {camera_name} at {ts}")
                if self.callback:
                    self.callback(camera_name, ts)
                time.sleep(self.debounce_sec)  # debounce
            time.sleep(0.1)
        logging.info(f"Watcher stopped for {camera_name}")

    def start(self):
        self._stop_event.clear()
        for cam, pin in self.sensor_config.items():
            t = threading.Thread(target=self._watch_sensor, args=(cam, pin), daemon=True)
            t.start()
            self._threads.append(t)
        logging.info("MotionDetector started.")

    def stop(self):
        self._stop_event.set()
        for t in self._threads:
            t.join()
        if ON_PI:
            GPIO.cleanup()
        logging.info("MotionDetector stopped and cleaned up.")

    def register_callback(self, callback):
        self.callback = callback

# Example usage
if __name__ == "__main__":
    import json
    with open("devices/nutpod/config.json") as f:
        config = json.load(f)
    sensor_cfg = config.get("motion_sensors", {"CritterCam": 17, "NestCam": 27})
    def print_cb(cam, ts):
        print(f"[EXAMPLE] Motion: {cam} at {ts}")
    md = MotionDetector(sensor_cfg, callback=print_cb)
    md.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        md.stop()

"""
MotionDetector: Detects motion in CritterCam frames using frame differencing.
Supports sensitivity adjustment and cooldown debounce.
"""

import numpy as np
import cv2
from datetime import datetime, timedelta

class VisionMotionDetector:
    def __init__(self, motion_sensitivity: float = 0.4, cooldown_sec: float = 1.0):
        self.motion_sensitivity = motion_sensitivity
        self.cooldown = timedelta(seconds=cooldown_sec)
        self.last_motion_time = None
        self.last_frame = None
        self.last_detection = False
        self.last_detection_time = None

    def detect_motion(self, frame: np.ndarray) -> bool:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        motion = False
        now = datetime.now()
        if self.last_frame is not None:
            # Compute absolute difference
            frame_delta = cv2.absdiff(self.last_frame, gray)
            thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
            motion_pixels = np.sum(thresh > 0)
            total_pixels = thresh.size
            motion_ratio = motion_pixels / total_pixels
            if motion_ratio > self.motion_sensitivity:
                # Debounce: only trigger if cooldown passed
                if not self.last_detection or (now - self.last_detection_time) > self.cooldown:
                    motion = True
                    self.last_motion_time = now
                    self.last_detection_time = now
                    self.last_detection = True
                    print(f"[VisionMotionDetector] ✅ Motion detected! Motion ratio: {motion_ratio:.3f} (threshold: {self.motion_sensitivity})")
            else:
                self.last_detection = False
        self.last_frame = gray
        return motion

    def get_last_motion_time(self) -> datetime:
        return self.last_motion_time
