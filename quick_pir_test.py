#!/usr/bin/env python3
"""
Quick PIR Test - Test PIR detection without Flask
"""

import sys
import os
import time

# Add the parent directory to Python path so we can import 'core'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_callback(camera_name: str, motion_event: dict):
    """Simple test callback"""
    print(f"🎯 TEST CALLBACK: {camera_name} detected motion!")
    print(f"   Event data: {motion_event}")
    print("=" * 50)

def main():
    print("🚨 Quick PIR Test Starting...")
    
    try:
        from core.motion.dual_pir_motion_detector import DualPIRMotionDetector
        print("✅ PIR detector imported successfully")
        
        # Create detector with test callback
        detector = DualPIRMotionDetector(motion_callback=test_callback)
        print("✅ PIR detector created")
        
        # Start detection
        detector.start_detection()
        print("✅ PIR detection started")
        print("🔍 Wave your hand in front of the PIR sensors for 30 seconds...")
        
        # Run for 30 seconds
        time.sleep(30)
        
        # Stop detection
        detector.stop_detection()
        print("✅ PIR detection stopped")
        
    except ImportError as e:
        print(f"❌ Failed to import PIR detector: {e}")
    except Exception as e:
        print(f"❌ PIR test failed: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")

if __name__ == '__main__':
    main()
