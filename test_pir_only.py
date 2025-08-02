#!/usr/bin/env python3
"""Just test PIR sensors - nothing else"""

print("🔍 PIR Motion Sensor Test")
print("=" * 50)
print("This will watch for motion for 10 seconds")
print("Wave your hand in front of the sensors!")
print()

import time

try:
    from gpiozero import Button
    
    # Setup PIR sensors
    critter_pir = Button(18, pull_up=False)  # Pin 12
    nest_pir = Button(12, pull_up=False)     # Pin 32
    
    print("✅ PIR sensors ready:")
    print("📍 CritterCam PIR: GPIO 18 (Pin 12)")  
    print("📍 NestCam PIR: GPIO 12 (Pin 32)")
    print()
    
    motion_count = 0
    
    def motion_detected(sensor_name):
        global motion_count
        motion_count += 1
        print(f"🚨 {sensor_name}: MOTION #{motion_count}!")
    
    critter_pir.when_pressed = lambda: motion_detected("CritterCam")
    nest_pir.when_pressed = lambda: motion_detected("NestCam")
    
    print("👋 Wave your hand around the sensors...")
    for i in range(10, 0, -1):
        print(f"⏰ {i} seconds left...", end='\r')
        time.sleep(1)
    
    print(f"\n🎯 Test complete! Detected {motion_count} motion events")
    
    if motion_count > 0:
        print("✅ PIR sensors are working!")
    else:
        print("❌ No motion detected")
        print("Check wiring: VCC->3.3V, GND->GND, OUT->GPIO pin")
        
except Exception as e:
    print(f"❌ PIR test error: {e}")
    print("Make sure PIR sensors are wired correctly")
