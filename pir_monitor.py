#!/usr/bin/env python3
"""
Simple PIR motion monitor that integrates with Flask sighting service
"""
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import time
import threading
from datetime import datetime
from core.motion.dual_pir_motion_detector import DualPIRMotionDetector
from core.sighting_service import sighting_service

def handle_pir_motion(camera_name, motion_event):
    """Handle PIR motion detection - record to database via sighting service"""
    print(f"🚨 PIR Motion detected on {camera_name}!")
    
    # Record motion event in database
    timestamp = datetime.now().isoformat()
    motion_data = {
        'camera': camera_name,
        'type': 'gpio',
        'confidence': 0.9,
        'duration': 2.0
    }
    
    try:
        sighting_service._record_motion_event(timestamp, motion_data)
        print(f"✅ Motion event recorded to database for {camera_name}")
    except Exception as e:
        print(f"❌ Error recording motion event: {e}")

def main():
    print("🎯 Starting PIR Motion Monitor")
    print("This will monitor PIR sensors and record events to the database")
    print("Press Ctrl+C to stop")
    
    # Initialize PIR detector with our callback
    pir_detector = DualPIRMotionDetector(motion_callback=handle_pir_motion)
    
    try:
        pir_detector.start()
        print("✅ PIR motion detection started")
        
        # Keep running
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping PIR motion detection...")
        pir_detector.stop()
        print("👋 PIR motion detection stopped")

if __name__ == '__main__':
    main()
