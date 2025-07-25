
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
            # Generate colorful mock frame instead of black frame
            import time
            import cv2
            
            # Create a 640x480 synthetic frame
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            
            # Different background colors for different cameras based on index
            if self.idx == 0:  # CritterCam
                # Forest scene - green/brown tones
                frame[:] = [40, 80, 40]  # Dark green background
                
                # Add some "trees" (vertical rectangles)
                cv2.rectangle(frame, (50, 200), (80, 480), (20, 60, 30), -1)
                cv2.rectangle(frame, (500, 150), (530, 480), (25, 65, 35), -1)
                
                # Add a moving "squirrel" (yellow circle)
                t = time.time()
                x = int(300 + 100 * np.sin(t * 0.5))
                y = int(250 + 50 * np.cos(t * 0.3))
                cv2.circle(frame, (x, y), 15, (0, 200, 255), -1)  # Yellow
                
                # Add some "leaves" (green dots)
                for i in range(10):
                    lx = int(100 + 400 * np.sin(t * 0.2 + i))
                    ly = int(100 + 200 * np.cos(t * 0.15 + i))
                    cv2.circle(frame, (lx, ly), 3, (0, 150, 50), -1)
                    
                camera_name = "CritterCam"
                    
            else:  # NestCam (idx == 1)
                # Sky/nest scene - blue/brown tones
                frame[:] = [100, 60, 30]  # Sky blue background
                
                # Add a "nest" (brown oval)
                cv2.ellipse(frame, (320, 350), (80, 40), 0, 0, 360, (30, 100, 150), -1)
                
                # Add moving "bird" (red dot)
                t = time.time()
                x = int(320 + 150 * np.sin(t * 0.8))
                y = int(200 + 80 * np.cos(t * 0.6))
                cv2.circle(frame, (x, y), 12, (0, 0, 200), -1)  # Red
                
                # Add "branches" (brown lines)
                cv2.line(frame, (0, 300), (640, 320), (30, 60, 100), 5)
                cv2.line(frame, (200, 100), (400, 280), (25, 55, 95), 3)
                
                camera_name = "NestCam"
            
            # Add timestamp overlay
            timestamp = time.strftime("%H:%M:%S", time.localtime())
            cv2.putText(frame, timestamp, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Add camera name overlay
            cv2.putText(frame, camera_name, (10, 460), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            return frame
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
            else:
                cam = MockCamera(idx)
                self.cameras[name] = cam
                print(f"[CameraManager] ✓ {name} initialized in mock mode")
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
