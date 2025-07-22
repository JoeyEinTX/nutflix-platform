
"""
CameraManager: Loads device config, initializes CritterCam and NestCam using Picamera2,
provides get_frame(camera_name), start_preview(), stop_preview(), and handles missing cameras.
"""


import numpy as np
from core.config.config_manager import get_config, ConfigError

# Try to import Picamera2; if unavailable, use a mock fallback
try:
    from picamera2 import Picamera2, Preview
    PICAMERA2_AVAILABLE = True
except ImportError:
    PICAMERA2_AVAILABLE = False

    class MockCamera:
        def __init__(self, idx):
            self.idx = idx
            print(f"[MockCamera] Camera index {idx} initialized (mock mode)")
        def configure(self, *args, **kwargs):
            pass
        def start(self):
            print(f"[MockCamera] start() called (mock mode)")
        def capture_array(self):
            print(f"[MockCamera] capture_array() called (mock mode)")
            # Return a black frame (480p)
            return np.zeros((480, 640, 3), dtype=np.uint8)
        def start_preview(self, *args, **kwargs):
            print(f"[MockCamera] start_preview() called (mock mode)")
        def stop_preview(self):
            print(f"[MockCamera] stop_preview() called (mock mode)")

class CameraManager:
    def __init__(self, device_name: str):
        try:
            self.config = get_config(device_name)
        except ConfigError as e:
            raise RuntimeError(f"Failed to load config for {device_name}: {e}")
        self.cameras = {}
        self.previews = {}
        enabled = self.config.get("enabled_cameras", [])
        # Map logical names to Picamera2 indexes (assume 0: CritterCam, 1: NestCam)
        cam_map = {"CritterCam": 0, "NestCam": 1}
        for name in enabled:
            idx = cam_map.get(name)
            if idx is not None:
                try:
                    if PICAMERA2_AVAILABLE:
                        cam = Picamera2(idx)
                        cam.configure(cam.create_still_configuration())
                        cam.start()
                    else:
                        cam = MockCamera(idx)
                    self.cameras[name] = cam
                except Exception as e:
                    print(f"Warning: Could not initialize {name} (index {idx}): {e}")
            else:
                print(f"Warning: Unknown camera name '{name}' in config.")

    def get_frame(self, camera_name: str) -> np.ndarray:
        cam = self.cameras.get(camera_name)
        if not cam:
            raise ValueError(f"Camera '{camera_name}' not initialized or not enabled.")
        try:
            frame = cam.capture_array()
            return frame
        except Exception as e:
            raise RuntimeError(f"Failed to capture frame from {camera_name}: {e}")

    def start_preview(self, camera_name: str):
        cam = self.cameras.get(camera_name)
        if not cam:
            print(f"Preview: Camera '{camera_name}' not initialized.")
            return
        if camera_name in self.previews:
            print(f"Preview already running for {camera_name}.")
            return
        try:
            if PICAMERA2_AVAILABLE:
                self.previews[camera_name] = cam.start_preview(Preview.QT)
            else:
                cam.start_preview()
        except Exception as e:
            print(f"Failed to start preview for {camera_name}: {e}")

    def stop_preview(self, camera_name: str):
        cam = self.cameras.get(camera_name)
        if not cam:
            print(f"Stop Preview: Camera '{camera_name}' not initialized.")
            return
        try:
            cam.stop_preview()
            self.previews.pop(camera_name, None)
        except Exception as e:
            print(f"Failed to stop preview for {camera_name}: {e}")
