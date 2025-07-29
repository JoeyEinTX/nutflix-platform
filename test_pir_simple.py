#!/usr/bin/env python3
"""
Simple PIR Motion Detection Test
Just tests the PIR sensors with recording triggers
"""

import sys
import os
sys.path.append('/home/p12146/NutFlix/nutflix-platform')

import time
import logging
from core.motion.dual_pir_motion_detector import DualPIRMotionDetector

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

def motion_callback(camera_name, motion_event):
    """Handle PIR motion detection"""
    timestamp = motion_event.get('timestamp', 'Unknown')
    gpio_pin = motion_event.get('gpio_pin', 'Unknown')
    
    print(f"🚨 MOTION DETECTED!")
    print(f"   Camera: {camera_name}")
    print(f"   GPIO: {gpio_pin}")
    print(f"   Time: {timestamp}")
    print(f"   → Would trigger recording for {camera_name}")
    print("-" * 50)

def main():
    print("🎯 PIR Motion Detection Test")
    print("=" * 50)
    print("✅ PIR Sensors:")
    print("   CritterCam → GPIO 18 (Pin 12)")
    print("   NestCam    → GPIO 24 (Pin 18)")
    print()
    print("👋 Wave your hand in front of sensors...")
    print("🛑 Press Ctrl+C to stop")
    print("=" * 50)
    
    # Initialize PIR detector
    pir_detector = DualPIRMotionDetector(motion_callback=motion_callback)
    pir_detector.start_detection()
    
    try:
        # Run indefinitely
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping PIR detection...")
        pir_detector.stop_detection()
        print("✅ PIR detection stopped")

if __name__ == "__main__":
    main()
