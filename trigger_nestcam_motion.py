#!/usr/bin/env python3
"""
Trigger NestCam motion to activate smart IR LED
"""

import sys
import os
import subprocess
import time
import json

def run_curl(url):
    """Run curl command and return JSON response"""
    try:
        result = subprocess.run(['curl', '-s', url], capture_output=True, text=True)
        return json.loads(result.stdout)
    except Exception as e:
        print(f"Error with curl: {e}")
        return None

def trigger_nestcam_motion():
    print("🎥 Triggering NestCam Motion Detection...")
    
    # First, check the API status
    status = run_curl("http://localhost:8000/api/motion/status")
    
    if status:
        print("📊 Current Status:")
        print(f"   Motion Detection: {'Running' if status['running'] else 'Stopped'}")
        print(f"   IR Available: {status['ir_status']['ir_available']}")
        print(f"   IR Active: {status['ir_status']['is_active']}")
        print(f"   Supported Cameras: {status['ir_status']['supported_cameras']}")
        
        # Since we can't directly trigger NestCam motion, let's try the general trigger
        print("\n🎲 Triggering test motions (trying to hit NestCam)...")
        
        for attempt in range(10):  # Try 10 times to get NestCam
            trigger_data = run_curl("http://localhost:8000/api/motion/trigger-test")
            
            if trigger_data and 'sighting' in trigger_data:
                camera = trigger_data['sighting']['camera']
                print(f"   Attempt {attempt + 1}: Motion on {camera}")
                
                if camera == "NestCam":
                    print("🎯 Hit NestCam! Checking IR status...")
                    time.sleep(2)  # Give it time to process
                    
                    # Check status again
                    new_status = run_curl("http://localhost:8000/api/motion/status")
                    
                    if new_status:
                        print(f"   IR Active Now: {new_status['ir_status']['is_active']}")
                        print(f"   Current Camera: {new_status['ir_status'].get('current_camera', 'None')}")
                        
                        if new_status['ir_status']['is_active']:
                            print("🔦 SUCCESS! IR LED should be ON now!")
                            print("👀 The IR LED should be illuminating the scene!")
                        else:
                            print("⚠️  IR didn't activate (might be daylight conditions)")
                    break
                    
            time.sleep(0.5)
        else:
            print("😅 Didn't hit NestCam in 10 attempts")
        
        print(f"\n🌐 View your camera feeds at:")
        print(f"   📹 Main Dashboard: http://localhost:8000")
        print(f"   📷 NestCam Direct: http://localhost:8000/api/stream/NestCam")
        print(f"   📷 CritterCam Direct: http://localhost:8000/api/stream/CritterCam")
        print(f"\n💡 TIP: Wave your hand in front of the NestCam to trigger real motion detection!")

if __name__ == "__main__":
    trigger_nestcam_motion()
