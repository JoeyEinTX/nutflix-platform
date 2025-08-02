#!/usr/bin/env python3
"""
Nutflix Platform - Simple Sensor Test for Raspberry Pi 5
Works with the newer GPIO libraries on Pi 5
"""

import sys
import time
import os

# Add project root to path
sys.path.insert(0, '/home/p12146/Projects/Nutflix-platform')

def test_i2c_scan():
    """Scan for I2C devices"""
    print("\n🔍 Scanning for I2C Devices")
    print("=" * 50)
    
    try:
        import subprocess
        result = subprocess.run(['i2cdetect', '-y', '1'], 
                              capture_output=True, text=True, check=False)
        
        if result.returncode == 0:
            print("✅ I2C scan results:")
            print(result.stdout)
            
            # Check for common sensor addresses
            output = result.stdout
            if '76' in output or '77' in output:
                print("🌡️  BME280 sensor detected at address 0x76 or 0x77!")
            else:
                print("❌ No BME280 sensor found")
                print("   Make sure it's wired: VCC->3.3V, GND->GND, SDA->Pin3, SCL->Pin5")
        else:
            print("❌ I2C not enabled or no devices found")
            print("   Run: sudo raspi-config -> Interface Options -> I2C -> Enable")
            
    except FileNotFoundError:
        print("❌ i2c-tools not installed")
        print("   Install with: sudo apt install i2c-tools")
    except Exception as e:
        print(f"❌ I2C scan error: {e}")

def test_pir_simple():
    """Simple PIR test using gpiozero"""
    print("\n🔍 Testing PIR Motion Sensors (gpiozero)")
    print("=" * 50)
    
    try:
        from gpiozero import Button
        from signal import pause
        import threading
        
        # PIR sensor pins
        CRITTER_PIR = 18  # Pin 12
        NEST_PIR = 12     # Pin 32
        
        # Create button objects for PIR sensors
        critter_pir = Button(CRITTER_PIR, pull_up=False)
        nest_pir = Button(NEST_PIR, pull_up=False)
        
        print("✅ PIR sensors initialized")
        print("📍 CritterCam PIR on GPIO 18 (Pin 12)")
        print("📍 NestCam PIR on GPIO 12 (Pin 32)")
        print("\n👋 Wave your hand in front of sensors...")
        print("Press Ctrl+C to stop")
        
        def critter_motion():
            print("🐿️  CritterCam PIR: MOTION DETECTED!")
            
        def nest_motion():
            print("🏠 NestCam PIR: MOTION DETECTED!")
        
        # Set up callbacks
        critter_pir.when_pressed = critter_motion
        nest_pir.when_pressed = nest_motion
        
        # Wait for motion for 30 seconds
        start_time = time.time()
        while time.time() - start_time < 30:
            time.sleep(0.1)
            
        print("\n✅ PIR test completed")
        
    except ImportError:
        print("❌ gpiozero not available")
        print("   Install with: pip install gpiozero")
    except Exception as e:
        print(f"❌ PIR test error: {e}")
        print("   Make sure PIR sensors are wired correctly")

def test_bme280_simple():
    """Simple BME280 test"""
    print("\n🌡️  Testing BME280 Environmental Sensor")
    print("=" * 50)
    
    try:
        # First try with the venv libraries
        import board
        import adafruit_bme280
        
        # Create I2C interface
        i2c = board.I2C()
        bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)
        
        print("✅ BME280 connected successfully!")
        print("📊 Reading sensor data...")
        
        for i in range(3):
            temp = bme280.temperature
            humidity = bme280.relative_humidity
            pressure = bme280.pressure
            
            print(f"🌡️  Temperature: {temp:.1f}°C")
            print(f"💧 Humidity: {humidity:.1f}%")
            print(f"📈 Pressure: {pressure:.1f} hPa")
            print("-" * 30)
            time.sleep(1)
            
    except Exception as e:
        print(f"❌ BME280 error: {e}")
        print("   Check wiring: SDA->Pin 3, SCL->Pin 5, VCC->3.3V, GND->GND")
        print("   Make sure I2C is enabled: sudo raspi-config -> Interface Options -> I2C")

def test_gpio_basic():
    """Test basic GPIO functionality"""
    print("\n💡 Testing Basic GPIO")
    print("=" * 50)
    
    try:
        from gpiozero import LED
        
        # Test with IR LED pin
        led = LED(23)  # GPIO 23, Pin 16
        
        print("✅ GPIO initialized successfully")
        print("💡 Testing GPIO 23 (Pin 16) - IR LED pin")
        print("   Blinking for 5 seconds...")
        
        for i in range(5):
            led.on()
            print(f"🔴 GPIO 23 HIGH ({i+1}/5)")
            time.sleep(0.5)
            led.off()
            print(f"⚫ GPIO 23 LOW ({i+1}/5)")
            time.sleep(0.5)
            
        led.close()
        print("✅ GPIO test completed")
        
    except Exception as e:
        print(f"❌ GPIO test error: {e}")

def show_simple_wiring():
    """Show simplified wiring guide"""
    print("\n📋 SIMPLIFIED WIRING GUIDE FOR PI 5")
    print("=" * 60)
    print("""
🔌 For your 6-pin BME280 sensor:
   Pin 1: VCC/VIN → Pi Pin 1 (3.3V)
   Pin 2: GND     → Pi Pin 6 (GND)  
   Pin 3: SCL     → Pi Pin 5 (GPIO 3)
   Pin 4: SDA     → Pi Pin 3 (GPIO 2)
   Pin 5: CSB/CS  → Leave unconnected
   Pin 6: SDO/SA0 → Leave unconnected (or connect to GND)

🔍 PIR Motion Sensors (connect one at a time to test):
   CritterCam PIR: VCC → Pin 1 (3.3V)
                   GND → Pin 6 (GND)
                   OUT → Pin 12 (GPIO 18)

💡 IR LED (for testing GPIO):
                   VCC → Pin 2 (5V)
                   GND → Pin 6 (GND)  
                   SIG → Pin 16 (GPIO 23)

📍 Pi 5 GPIO Layout (key pins):
   Pin 1  [3.3V] ● ● [5V     ] Pin 2
   Pin 3  [SDA ] ● ● [5V     ] Pin 4
   Pin 5  [SCL ] ● ● [Ground ] Pin 6
   ...
   Pin 12 [GPIO18] ● ● [     ] Pin 13  ← CritterCam PIR
   ...
   Pin 16 [GPIO23] ● ● [     ] Pin 17  ← IR LED
    """)

def main():
    """Simple test menu"""
    print("🐿️ Nutflix Platform - Simple Pi 5 Sensor Tests")
    print("=" * 60)
    
    while True:
        print("\nQuick Tests:")
        print("1. Show wiring guide")
        print("2. Scan for I2C devices (BME280)")
        print("3. Test BME280 sensor readings")
        print("4. Test PIR motion sensors")
        print("5. Test basic GPIO (IR LED)")
        print("6. Run all tests")
        print("7. Exit")
        
        try:
            choice = input("\nEnter choice (1-7): ").strip()
            
            if choice == "1":
                show_simple_wiring()
            elif choice == "2":
                test_i2c_scan()
            elif choice == "3":
                test_bme280_simple()
            elif choice == "4":
                test_pir_simple()
            elif choice == "5":
                test_gpio_basic()
            elif choice == "6":
                test_i2c_scan()
                test_bme280_simple()
                test_pir_simple()
                test_gpio_basic()
            elif choice == "7":
                print("👋 Goodbye!")
                break
            else:
                print("Please enter 1-7")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break

if __name__ == "__main__":
    main()
