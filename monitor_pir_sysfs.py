#!/usr/bin/env python3
"""
PIR Sensor State Monitor using /sys/class/gpio
Monitor PIR sensor states without interfering with the main system
"""

import time
import os

def read_gpio_value(pin):
    """Read GPIO pin value from /sys/class/gpio"""
    try:
        with open(f'/sys/class/gpio/gpio{pin}/value', 'r') as f:
            return int(f.read().strip())
    except (FileNotFoundError, PermissionError, ValueError):
        return None

def monitor_pir_sensors(duration=30):
    """Monitor PIR sensors for the specified duration"""
    print(f"🔍 Monitoring PIR sensors for {duration} seconds...")
    print("📍 CritterCam: GPIO 18, NestCam: GPIO 24")
    print("📝 State: 0=LOW (no motion), 1=HIGH (motion detected)")
    print("🕐 Move in front of the sensors to test...")
    print()
    
    # Check if GPIO pins are accessible
    gpio18_available = os.path.exists('/sys/class/gpio/gpio18/value')
    gpio24_available = os.path.exists('/sys/class/gpio/gpio24/value')
    
    if not gpio18_available:
        print("⚠️  GPIO 18 not available in /sys/class/gpio (may be claimed by running system)")
    if not gpio24_available:
        print("⚠️  GPIO 24 not available in /sys/class/gpio (may be claimed by running system)")
    
    if not gpio18_available and not gpio24_available:
        print("❌ Neither GPIO pin is accessible via /sys/class/gpio")
        print("💡 This is expected if the main system is using lgpio library")
        return
    
    start_time = time.time()
    last_critter_state = None
    last_nest_state = None
    detection_count = {'CritterCam': 0, 'NestCam': 0}
    
    while time.time() - start_time < duration:
        # Read current states
        critter_state = read_gpio_value(18) if gpio18_available else None
        nest_state = read_gpio_value(24) if gpio24_available else None
        
        # Check for state changes
        current_time = time.strftime('%H:%M:%S')
        
        if gpio18_available and critter_state != last_critter_state and critter_state is not None:
            state_name = "HIGH" if critter_state else "LOW"
            print(f"[{current_time}] 🟡 CritterCam (GPIO 18): {state_name} ({critter_state})")
            if critter_state == 1:  # Rising edge
                detection_count['CritterCam'] += 1
                print(f"[{current_time}] 🚨 CritterCam MOTION #{detection_count['CritterCam']}")
            last_critter_state = critter_state
            
        if gpio24_available and nest_state != last_nest_state and nest_state is not None:
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
    if gpio18_available:
        final_critter = read_gpio_value(18)
        print(f"🔍 Final CritterCam state: {final_critter}")
    if gpio24_available:
        final_nest = read_gpio_value(24)
        print(f"🔍 Final NestCam state: {final_nest}")

if __name__ == "__main__":
    try:
        monitor_pir_sensors(30)  # Monitor for 30 seconds
    except KeyboardInterrupt:
        print("\n⏹️ Monitoring stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
