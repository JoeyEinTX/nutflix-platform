#!/usr/bin/env python3
"""
PIR Sensor State Monitor
Monitor PIR sensor states without interfering with the main system
"""

import time
import subprocess
import sys

def get_gpio_state(pin):
    """Get GPIO pin state using gpio command instead of Python GPIO"""
    try:
        result = subprocess.run(['gpio', 'read', str(pin)], 
                              capture_output=True, text=True, timeout=2)
        if result.returncode == 0:
            return int(result.stdout.strip())
        else:
            return None
    except (subprocess.TimeoutExpired, FileNotFoundError, ValueError):
        return None

def monitor_pir_sensors(duration=60):
    """Monitor PIR sensors for the specified duration"""
    print(f"🔍 Monitoring PIR sensors for {duration} seconds...")
    print("📍 CritterCam: GPIO 18, NestCam: GPIO 24")
    print("📝 State: 0=LOW (no motion), 1=HIGH (motion detected)")
    print("🕐 Move in front of the sensors to test...")
    print()
    
    start_time = time.time()
    last_critter_state = None
    last_nest_state = None
    detection_count = {'CritterCam': 0, 'NestCam': 0}
    
    while time.time() - start_time < duration:
        # Read current states
        critter_state = get_gpio_state(18)
        nest_state = get_gpio_state(24)
        
        # Check for state changes
        current_time = time.strftime('%H:%M:%S')
        
        if critter_state != last_critter_state and critter_state is not None:
            state_name = "HIGH" if critter_state else "LOW"
            print(f"[{current_time}] 🟡 CritterCam (GPIO 18): {state_name} ({critter_state})")
            if critter_state == 1:  # Rising edge
                detection_count['CritterCam'] += 1
                print(f"[{current_time}] 🚨 CritterCam MOTION #{detection_count['CritterCam']}")
            last_critter_state = critter_state
            
        if nest_state != last_nest_state and nest_state is not None:
            state_name = "HIGH" if nest_state else "LOW"
            print(f"[{current_time}] 🔵 NestCam (GPIO 24): {state_name} ({nest_state})")
            if nest_state == 1:  # Rising edge
                detection_count['NestCam'] += 1
                print(f"[{current_time}] 🚨 NestCam MOTION #{detection_count['NestCam']}")
            last_nest_state = nest_state
        
        time.sleep(0.2)  # Check every 200ms
    
    print(f"\n📊 Final Results ({duration}s):")
    print(f"🟡 CritterCam detections: {detection_count['CritterCam']}")
    print(f"🔵 NestCam detections: {detection_count['NestCam']}")
    
    # Show final states
    final_critter = get_gpio_state(18)
    final_nest = get_gpio_state(24)
    print(f"🔍 Final States: CritterCam={final_critter}, NestCam={final_nest}")

if __name__ == "__main__":
    try:
        # Check if gpio command is available
        subprocess.run(['gpio', '-v'], capture_output=True, timeout=2)
        monitor_pir_sensors(30)  # Monitor for 30 seconds
    except FileNotFoundError:
        print("❌ 'gpio' command not found. Install with: sudo apt install wiringpi")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️ Monitoring stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
