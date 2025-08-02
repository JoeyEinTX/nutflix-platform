#!/usr/bin/env python3
"""
Super Simple Sensor Tests - No confusing menus!
Just run specific tests directly
"""

import time
import sys

def test_bme280_now():
    """Test BME280 right now - no menu"""
    print("🌡️ Testing BME280 Environmental Sensor")
    print("=" * 50)
    
    # First check if it's detected on I2C
    import subprocess
    result = subprocess.run(['i2cdetect', '-y', '1'], capture_output=True, text=True)
    
    if '76' in result.stdout or '77' in result.stdout:
        print("✅ BME280 detected on I2C bus!")
        
        try:
            import board
            import adafruit_bme280
            
            i2c = board.I2C()
            bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)
            
            print("📊 Reading data...")
            temp = bme280.temperature
            humidity = bme280.relative_humidity  
            pressure = bme280.pressure
            
            print(f"🌡️ Temperature: {temp:.1f}°C ({temp*9/5+32:.1f}°F)")
            print(f"💧 Humidity: {humidity:.1f}%")
            print(f"📈 Pressure: {pressure:.1f} hPa")
            print("✅ BME280 is working!")
            
        except Exception as e:
            print(f"❌ BME280 library error: {e}")
    else:
        print("❌ No BME280 found on I2C")
        print("Wire it up: VCC->Pin1, GND->Pin6, SDA->Pin3, SCL->Pin5")

def test_pir_now():
    """Test PIR sensors right now - no confusing menu"""
    print("🔍 Testing PIR Motion Sensors")
    print("=" * 50)
    print("This will watch for motion for 15 seconds...")
    print("Wave your hand in front of the sensors!")
    
    try:
        from gpiozero import Button
        
        # PIR pins
        critter_pir = Button(18, pull_up=False)  # Pin 12
        nest_pir = Button(12, pull_up=False)     # Pin 32
        
        print("✅ PIR sensors initialized")
        print("📍 CritterCam PIR: GPIO 18 (Pin 12)")
        print("📍 NestCam PIR: GPIO 12 (Pin 32)")
        print("\n👋 Watching for motion...")
        
        motion_detected = False
        
        def critter_motion():
            nonlocal motion_detected
            motion_detected = True
            print("🐿️ CritterCam PIR: MOTION DETECTED!")
            
        def nest_motion():
            nonlocal motion_detected
            motion_detected = True
            print("🏠 NestCam PIR: MOTION DETECTED!")
        
        critter_pir.when_pressed = critter_motion
        nest_pir.when_pressed = nest_motion
        
        # Watch for 15 seconds
        for i in range(15):
            print(f"⏰ {15-i} seconds remaining...", end='\r')
            time.sleep(1)
            
        print("\n")
        if motion_detected:
            print("✅ PIR sensors are working!")
        else:
            print("❌ No motion detected - check wiring")
            
    except Exception as e:
        print(f"❌ PIR error: {e}")

def test_gpio_blink():
    """Test basic GPIO by blinking an LED"""
    print("💡 Testing GPIO with LED Blink")
    print("=" * 50)
    
    try:
        from gpiozero import LED
        
        led = LED(23)  # GPIO 23, Pin 16
        print("✅ Blinking GPIO 23 (Pin 16) - IR LED pin")
        print("If you have an LED connected, you should see it blink")
        
        for i in range(10):
            led.on()
            print(f"🔴 ON  ({i+1}/10)")
            time.sleep(0.5)
            led.off()
            print(f"⚫ OFF ({i+1}/10)")
            time.sleep(0.5)
            
        led.close()
        print("✅ GPIO test complete!")
        
    except Exception as e:
        print(f"❌ GPIO error: {e}")

def check_cameras():
    """Check what cameras are available"""
    print("📷 Checking for Cameras")
    print("=" * 50)
    
    try:
        # Try different camera detection methods
        import subprocess
        
        # Method 1: Try picamera2
        try:
            from picamera2 import Picamera2
            picam2 = Picamera2()
            camera_info = picam2.camera_properties
            print("✅ Camera detected with picamera2!")
            print(f"📸 Camera info: {camera_info}")
            picam2.close()
            return True
        except Exception as e:
            print(f"❌ Picamera2 not working: {e}")
        
        # Method 2: Try listing video devices
        result = subprocess.run(['ls', '/dev/video*'], 
                              capture_output=True, text=True, check=False)
        if result.returncode == 0:
            print("✅ Video devices found:")
            print(result.stdout)
        else:
            print("❌ No video devices found")
            
        # Method 3: Check for camera modules
        result = subprocess.run(['lsmod'], capture_output=True, text=True)
        if 'camera' in result.stdout.lower():
            print("✅ Camera module loaded")
        else:
            print("❌ No camera module loaded")
            
    except Exception as e:
        print(f"❌ Camera check error: {e}")

if __name__ == "__main__":
    print("🐿️ Nutflix Platform - Direct Sensor Tests")
    print("=" * 60)
    print("Testing everything directly - no confusing menus!")
    print()
    
    # Test everything in order
    print("1️⃣ Checking I2C devices...")
    test_bme280_now()
    print()
    
    print("2️⃣ Testing cameras...")
    check_cameras()
    print()
    
    print("3️⃣ Testing GPIO...")
    test_gpio_blink()
    print()
    
    print("4️⃣ Testing PIR sensors...")
    test_pir_now()
    print()
    
    print("🎯 All tests complete!")
