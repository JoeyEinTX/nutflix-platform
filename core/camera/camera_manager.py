
"""
CameraManager: Loads device config, initializes CritterCam and NestCam using Picamera2,
provides get_frame(camera_name), start_preview(), stop_preview(), and handles missing cameras.
"""

import cv2
import numpy as np
from core.config.config_manager import get_config, ConfigError

# Try to import Picamera2; if unavailable, use a mock fallback
try:
    from picamera2 import Picamera2, Preview
    PICAMERA2_AVAILABLE = True
except ImportError:
    PICAMERA2_AVAILABLE = False
    print("⚠️ Picamera2 not available - camera functionality disabled")

class CameraManager:
    def __init__(self, device_name: str):
        try:
            self.config = get_config(device_name)
        except ConfigError as e:
            raise RuntimeError(f"Failed to load config for {device_name}: {e}")
        self.cameras = {}
        self.previews = {}
        self._initialize_cameras()
        
    def _initialize_cameras(self):
        """Initialize cameras with retry logic"""
        enabled = self.config.get("enabled_cameras", [])
        # Map logical names to Picamera2 indexes (assume 0: CritterCam, 1: NestCam)
        cam_map = {"CritterCam": 0, "NestCam": 1}
        
        for name in enabled:
            idx = cam_map.get(name)
            if idx is not None:
                self._init_single_camera(name, idx)
            else:
                print(f"Warning: Unknown camera name '{name}' in config.")
                
    def _init_single_camera(self, name: str, idx: int):
        """Initialize a single camera with error handling"""
        try:
            if PICAMERA2_AVAILABLE:
                print(f"[CameraManager] Initializing {name} at index {idx}")
                cam = Picamera2(idx)
                
                # Configure for still capture with proper color format
                still_config = cam.create_still_configuration(
                    main={"size": (640, 480), "format": "RGB888"},  # Use RGB888 for better color
                    encode="main"
                )
                cam.configure(still_config)
                cam.start()
                
                self.cameras[name] = cam
                print(f"[CameraManager] ✓ {name} initialized successfully at 640x480 RGB888")
        except Exception as e:
            print(f"[CameraManager] Warning: Could not initialize {name} (index {idx}): {e}")
            # Store the error for debugging
            self.cameras[name] = None

    def get_frame(self, camera_name: str) -> np.ndarray:
        cam = self.cameras.get(camera_name)
        if not cam:
            raise ValueError(f"Camera '{camera_name}' not initialized or not enabled.")
        if cam is None:  # Camera failed to initialize
            raise RuntimeError(f"Camera '{camera_name}' failed to initialize.")
        try:
            frame = cam.capture_array()
            if frame is None:
                raise RuntimeError(f"Camera '{camera_name}' returned None frame.")
            
            # Debug the frame format
            print(f"[CameraManager] {camera_name} frame shape: {frame.shape}, dtype: {frame.dtype}")
            
            # Convert RGB to BGR for proper web display
            # Picamera2 with RGB888 gives us RGB, but OpenCV/JPEG expects BGR
            if len(frame.shape) == 3 and frame.shape[2] == 3:
                frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                return frame_bgr
            
            return frame
        except Exception as e:
            print(f"[CameraManager] Error capturing from {camera_name}: {e}")
            raise RuntimeError(f"Failed to capture frame from {camera_name}: {e}")
            
    def is_camera_available(self, camera_name: str) -> bool:
        """Check if a camera is available and working"""
        cam = self.cameras.get(camera_name)
        return cam is not None and cam is not False
    
    def get_camera(self, camera_name: str):
        """Get camera instance for recording operations"""
        if camera_name not in self.cameras:
            return None
        
        camera = self.cameras[camera_name]
        if camera is None or camera is False:
            return None
            
        return camera
        
    def get_available_cameras(self) -> list:
        """Get list of successfully initialized cameras"""
        return [name for name, cam in self.cameras.items() if cam is not None]

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
