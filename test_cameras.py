#!/usr/bin/env python3
"""
Quick camera test for NutFlix platform
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from picamera2 import Picamera2
    PICAMERA_AVAILABLE = True
    print("✅ Picamera2 imported successfully")
except ImportError as e:
    PICAMERA_AVAILABLE = False
    print(f"❌ Picamera2 import failed: {e}")

def test_cameras():
    if not PICAMERA_AVAILABLE:
        print("Picamera2 not available - cannot test cameras")
        return False
    
    try:
        # Get camera info
        cameras = Picamera2.global_camera_info()
        print(f"📷 Found {len(cameras)} camera(s)")
        
        for i, cam_info in enumerate(cameras):
            print(f"  Camera {i}: {cam_info}")
        
        if len(cameras) == 0:
            print("❌ No cameras detected")
            return False
            
        # Test first camera
        print("\n🧪 Testing camera 0...")
        picam = Picamera2(0)
        config = picam.create_still_configuration(main={"size": (640, 480)})
        picam.configure(config)
        picam.start()
        print("✅ Camera 0 started successfully")
        
        # Test capture
        array = picam.capture_array()
        print(f"✅ Captured frame: {array.shape}")
        
        picam.stop()
        print("✅ Camera 0 stopped successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Camera test failed: {e}")
        return False

if __name__ == "__main__":
    print("🐿️ NutFlix Camera Test")
    print("=" * 30)
    success = test_cameras()
    sys.exit(0 if success else 1)
