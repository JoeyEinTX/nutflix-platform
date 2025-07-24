"""
Mock Camera Manager for NutFlix Platform
Provides mock camera functionality when real cameras are not available
"""

import cv2
import numpy as np
import time
from typing import Dict, Any

class MockCameraManager:
    """Mock camera manager that generates synthetic camera frames"""
    
    def __init__(self, device_name='nutpod'):
        self.device_name = device_name
        self.cameras = {
            'CritterCam': {
                'active': True,
                'last_frame_time': time.time()
            },
            'NestCam': {
                'active': True, 
                'last_frame_time': time.time()
            }
        }
        
    def get_frame(self, camera_name: str) -> np.ndarray:
        """Generate a mock camera frame"""
        
        # Create a 640x480 synthetic frame
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Different background colors for different cameras
        if camera_name == 'CritterCam':
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
                
        elif camera_name == 'NestCam':
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
        
        # Add timestamp overlay
        timestamp = time.strftime("%H:%M:%S", time.localtime())
        cv2.putText(frame, timestamp, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Add camera name overlay
        cv2.putText(frame, camera_name, (10, 460), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        return frame
        
    def get_camera_status(self, camera_name: str) -> Dict[str, Any]:
        """Get status of a specific camera"""
        if camera_name in self.cameras:
            return {
                'name': camera_name,
                'active': self.cameras[camera_name]['active'],
                'last_frame': self.cameras[camera_name]['last_frame_time'],
                'resolution': '640x480',
                'fps': 30
            }
        return {'name': camera_name, 'active': False}
        
    def list_cameras(self):
        """List all available cameras"""
        return list(self.cameras.keys())
