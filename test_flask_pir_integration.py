#!/usr/bin/env python3
"""
Test Flask PIR Integration - Test just the PIR startup part
"""

import sys
import os

# Add the parent directory to Python path so we can import 'core'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_pir_callback(camera_name: str, motion_event: dict):
    """Test callback"""
    print(f"🎯 FLASK TEST CALLBACK: {camera_name}")
    print(f"   Event: {motion_event}")

def main():
    print("🧪 Testing Flask PIR Integration Components...")
    
    # Test imports
    try:
        from core.motion.dual_pir_motion_detector import DualPIRMotionDetector
        print("✅ PIR detector import works")
        PIR_DETECTOR_AVAILABLE = True
    except ImportError as e:
        print(f"❌ PIR detector import failed: {e}")
        PIR_DETECTOR_AVAILABLE = False
    
    try:
        from core.sighting_service import sighting_service
        print("✅ Sighting service import works")
        SIGHTING_SERVICE_AVAILABLE = True
    except ImportError as e:
        print(f"❌ Sighting service import failed: {e}")
        SIGHTING_SERVICE_AVAILABLE = False
    
    # Test PIR initialization logic (same as Flask)
    if PIR_DETECTOR_AVAILABLE and SIGHTING_SERVICE_AVAILABLE:
        print("🚨 Would initialize PIR motion detection...")
        print(f"🔥 PIR_DETECTOR_AVAILABLE={PIR_DETECTOR_AVAILABLE}")
        print(f"🔥 SIGHTING_SERVICE_AVAILABLE={SIGHTING_SERVICE_AVAILABLE}")
        try:
            print("🔥 Creating DualPIRMotionDetector instance...")
            pir_detector = DualPIRMotionDetector(motion_callback=test_pir_callback)
            print("✅ PIR detector created successfully")
            print("🔥 Would call start_detection() in real Flask...")
            print("✅ PIR integration logic works!")
        except Exception as e:
            print(f"❌ Failed to create PIR detector: {e}")
            import traceback
            print(f"🔥 TRACEBACK: {traceback.format_exc()}")
    else:
        print(f"❌ PIR motion detection would NOT start:")
        print(f"   PIR_DETECTOR_AVAILABLE={PIR_DETECTOR_AVAILABLE}")
        print(f"   SIGHTING_SERVICE_AVAILABLE={SIGHTING_SERVICE_AVAILABLE}")

if __name__ == '__main__':
    main()
