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

# VisionMotionDetector removed - system now uses PIR sensors exclusively for motion detection
