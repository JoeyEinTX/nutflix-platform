#!/usr/bin/env python3
"""
PIR Motion Simulation Test - Test the full callback chain
"""

import sys
import os
from datetime import datetime

# Add the parent directory to Python path so we can import 'core'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    print("🔥 Testing PIR Motion Callback Chain...")
    
    # Import what we need
    try:
        from core.sighting_service import sighting_service
        print("✅ Sighting service imported")
    except ImportError as e:
        print(f"❌ Sighting service import failed: {e}")
        return
    
    # Create the same callback as in Flask
    def pir_motion_callback(camera_name: str, motion_event: dict):
        """Handle PIR motion detection events - same as Flask"""
        print(f"🔥 CALLBACK TRIGGERED! camera_name={camera_name}")
        print(f"🔥 CALLBACK motion_event={motion_event}")
        
        try:
            print(f"🚨 PIR Motion detected: {camera_name} - {motion_event}")
            
            # Create motion data compatible with sighting service
            motion_data = {
                'camera': camera_name,
                'motion_type': 'gpio',  # PIR sensor type
                'confidence': 0.95,     # PIR sensors are very reliable
                'detection_method': motion_event.get('detection_method', 'hardware_motion_sensor'),
                'sensor_type': motion_event.get('sensor_type', 'PIR'),
                'gpio_pin': motion_event.get('gpio_pin'),
                'trigger_type': motion_event.get('trigger_type', 'pir_motion')
            }
            
            print(f"🔥 CALLING _record_motion_event with motion_data={motion_data}")
            # Record the motion event
            timestamp = motion_event.get('timestamp')
            sighting_service._record_motion_event(timestamp, motion_data)
            print(f"✅ Motion event recorded to database: {camera_name}")
            
        except Exception as e:
            print(f"❌ Error handling PIR motion: {e}")
            import traceback
            print(f"🔥 FULL TRACEBACK: {traceback.format_exc()}")
    
    # Simulate a PIR motion event
    print("\n🎭 Simulating PIR motion event...")
    test_motion_event = {
        'timestamp': datetime.now().isoformat(),
        'camera_name': 'CritterCam',
        'sensor_type': 'AM312_PIR',
        'detection_method': 'hardware_motion_sensor',
        'trigger_type': 'pir_motion',
        'gpio_pin': 18,
        'motion_type': 'motion_start'
    }
    
    # Call the callback with test data
    pir_motion_callback('CritterCam', test_motion_event)
    
    print("\n🔍 Checking if motion appeared in database...")
    try:
        recent_sightings = sighting_service.get_recent_sightings(limit=1)
        if recent_sightings:
            latest = recent_sightings[0]
            print(f"✅ Latest sighting: {latest['camera']} at {latest['timestamp']}")
            print("🎯 SUCCESS: PIR callback → database → sightings API works!")
        else:
            print("❌ No recent sightings found")
    except Exception as e:
        print(f"❌ Error checking sightings: {e}")

if __name__ == '__main__':
    main()
