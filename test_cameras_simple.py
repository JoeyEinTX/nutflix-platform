#!/usr/bin/env python3
"""
Simple Camera Test for Nutflix Platform
"""

def test_cameras():
    print("📷 Testing Cameras on Pi 5")
    print("=" * 50)
    
    # Check video devices
    import os
    video_devices = []
    for i in range(50):
        device_path = f"/dev/video{i}"
        if os.path.exists(device_path):
            video_devices.append(device_path)
    
    print(f"Found video devices: {video_devices}")
    
    # Test with OpenCV
    try:
        import cv2
        print("\n🔍 Testing cameras with OpenCV...")
        
        working_cameras = []
        for i in range(5):
            print(f"Testing camera {i}...")
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    print(f"✅ Camera {i}: Working! Frame size: {frame.shape}")
                    working_cameras.append(i)
                    
                    # Try to save a test image
                    cv2.imwrite(f"/home/p12146/Projects/Nutflix-platform/test_camera_{i}.jpg", frame)
                    print(f"   Saved test image: test_camera_{i}.jpg")
                else:
                    print(f"❌ Camera {i}: No frame captured")
                cap.release()
            else:
                print(f"❌ Camera {i}: Could not open")
        
        print(f"\n✅ Working cameras: {working_cameras}")
        
    except ImportError:
        print("❌ OpenCV not available - install with: pip install opencv-python")
    except Exception as e:
        print(f"❌ Camera test error: {e}")

    # Test with picamera2 if available
    try:
        from picamera2 import Picamera2
        print("\n📷 Testing with Picamera2...")
        
        picam2 = Picamera2()
        print("✅ Picamera2 imported successfully!")
        
        # Get camera info
        try:
            camera_properties = picam2.camera_properties
            print(f"Camera properties: {camera_properties}")
        except Exception as e:
            print(f"⚠️  Could not get camera properties: {e}")
        
        # Try to configure and capture
        try:
            config = picam2.create_preview_configuration()
            picam2.configure(config)
            picam2.start()
            
            # Capture an image
            picam2.capture_file("/home/p12146/Projects/Nutflix-platform/test_picamera2.jpg")
            print("✅ Captured image with picamera2: test_picamera2.jpg")
            
            picam2.stop()
            picam2.close()
            
        except Exception as e:
            print(f"❌ Picamera2 capture error: {e}")
            
    except ImportError:
        print("❌ Picamera2 not available")
    except Exception as e:
        print(f"❌ Picamera2 error: {e}")

if __name__ == "__main__":
    test_cameras()
