#!/usr/bin/env python3
"""
Nutflix Platform - Sensor Testing Script
Test each sensor individually as you wire them up
"""

import sys
import time
import os

# Add project root to path
sys.path.insert(0, '/home/p12146/Projects/Nutflix-platform')

def test_pir_sensors():
    """Test PIR motion sensors"""
    print("\n🔍 Testing PIR Motion Sensors")
    print("=" * 50)
    
    try:
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM)
        
        # PIR sensor pins
        CRITTER_PIR = 18  # Pin 12
        NEST_PIR = 12     # Pin 32
        
        # Setup pins as inputs with pull-down
        GPIO.setup(CRITTER_PIR, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(NEST_PIR, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        
        print("✅ GPIO setup complete")
        print("📍 CritterCam PIR on GPIO 18 (Pin 12)")
        print("📍 NestCam PIR on GPIO 12 (Pin 32)")
        print("\n👋 Wave your hand in front of sensors...")
        print("Press Ctrl+C to stop")
        
        while True:
            critter_state = GPIO.input(CRITTER_PIR)
            nest_state = GPIO.input(NEST_PIR)
            
            if critter_state:
                print("🐿️  CritterCam PIR: MOTION DETECTED!")
            if nest_state:
                print("🏠 NestCam PIR: MOTION DETECTED!")
                
            time.sleep(0.1)
            
    except ImportError:
        print("❌ RPi.GPIO not available - install with: sudo apt install python3-rpi.gpio")
    except KeyboardInterrupt:
        print("\n✅ PIR test stopped")
    except Exception as e:
        print(f"❌ PIR test error: {e}")
    finally:
        try:
            GPIO.cleanup()
        except:
            pass

def test_bme280():
    """Test BME280 environmental sensor"""
    print("\n🌡️  Testing BME280 Environmental Sensor")
    print("=" * 50)
    
    try:
        import board
        from adafruit_bme280.basic import Adafruit_BME280_I2C
        
        # Create I2C interface
        i2c = board.I2C()
        # Try address 0x76 first (most common), then 0x77
        try:
            bme280_sensor = Adafruit_BME280_I2C(i2c, address=0x76)
        except:
            bme280_sensor = Adafruit_BME280_I2C(i2c, address=0x77)
        
        print("✅ BME280 connected successfully!")
        print("📊 Reading sensor data...")
        
        for i in range(5):
            temp_c = bme280_sensor.temperature
            temp_f = (temp_c * 9/5) + 32  # Convert to Fahrenheit
            humidity = bme280_sensor.relative_humidity
            pressure = bme280_sensor.pressure
            
            print(f"🌡️  Temperature: {temp_f:.1f}°F ({temp_c:.1f}°C)")
            print(f"💧 Humidity: {humidity:.1f}%")
            print(f"📈 Pressure: {pressure:.1f} hPa")
            print("-" * 30)
            time.sleep(2)
            
    except ImportError as ie:
        print(f"❌ BME280 library import error: {ie}")
        print("   Install with: pip install adafruit-circuitpython-bme280 adafruit-blinka")
    except Exception as e:
        print(f"❌ BME280 error: {e}")
        
        # Try to scan I2C for devices
        try:
            print("   Scanning I2C bus for devices...")
            import subprocess
            result = subprocess.run(['i2cdetect', '-y', '1'], capture_output=True, text=True)
            if result.returncode == 0:
                print("I2C scan results:")
                print(result.stdout)
                if '76' in result.stdout or '77' in result.stdout:
                    print("✅ BME280 detected on I2C bus at address 0x76 or 0x77")
                else:
                    print("❌ No BME280 found on I2C bus")
            else:
                print("❌ I2C scan failed")
        except Exception as scan_e:
            print(f"❌ I2C scan error: {scan_e}")
            
        print("   Check wiring: SDA->Pin 3, SCL->Pin 5, VCC->3.3V, GND->GND")
        print("   Make sure I2C is enabled: sudo raspi-config -> Interface Options -> I2C")

def test_ir_led():
    """Test IR LED controller"""
    print("\n💡 Testing IR LED Controller")
    print("=" * 50)
    
    try:
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM)
        
        IR_LED_PIN = 23  # Pin 16
        GPIO.setup(IR_LED_PIN, GPIO.OUT)
        
        print("✅ IR LED setup complete")
        print("💡 Blinking IR LED (GPIO 23, Pin 16)")
        print("   Note: IR light is invisible to human eyes")
        
        for i in range(10):
            GPIO.output(IR_LED_PIN, GPIO.HIGH)
            print(f"🔴 IR LED ON  ({i+1}/10)")
            time.sleep(1)
            GPIO.output(IR_LED_PIN, GPIO.LOW)
            print(f"⚫ IR LED OFF ({i+1}/10)")
            time.sleep(1)
            
    except ImportError:
        print("❌ RPi.GPIO not available")
    except Exception as e:
        print(f"❌ IR LED error: {e}")
    finally:
        try:
            GPIO.cleanup()
        except:
            pass

def test_microphone():
    """Test I2S microphone"""
    print("\n🎤 Testing I2S Microphone")
    print("=" * 50)
    
    try:
        import sounddevice as sd
        
        print("📻 Available audio devices:")
        devices = sd.query_devices()
        i2s_device = None
        for i, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                print(f"  {i}: {device['name']}")
                if 'googlevoicehat' in device['name'].lower():
                    i2s_device = i
        
        if i2s_device is None:
            print("❌ I2S microphone device not found")
            return
            
        print(f"\n🎵 Recording 3 seconds from I2S microphone (device {i2s_device})...")
        print("💬 Make some noise to test the microphone!")
        
        # I2S microphones need specific format: 48kHz, stereo, 32-bit
        sample_rate = 48000
        duration = 3
        
        # Record in stereo (I2S requirement) but we'll only use one channel
        recording = sd.rec(int(duration * sample_rate), 
                          samplerate=sample_rate, 
                          channels=2,
                          device=i2s_device,
                          dtype='float32')
        sd.wait()
        
        # Use left channel (microphone data is usually on left for SPH0645)
        left_channel = recording[:, 0]
        
        # Calculate volume level
        volume = abs(left_channel).mean()
        max_volume = abs(left_channel).max()
        
        print(f"✅ Recording complete!")
        print(f"📊 Average volume: {volume:.6f}")
        print(f"📊 Peak volume: {max_volume:.6f}")
        
        if volume > 0.001:
            print("🔊 Microphone is working - detected audio!")
        elif max_volume > 0.001:
            print("🔊 Microphone detected some signal - try talking louder!")
        else:
            print("🔇 Very quiet - check microphone wiring")
            print("   Expected wiring:")
            print("   VIN -> Pin 1 (3.3V), GND -> Pin 6 (GND)")
            print("   LRCL -> Pin 35 (GPIO 19), DOUT -> Pin 38 (GPIO 20)")
            print("   BCLK -> Pin 40 (GPIO 21), SEL -> Pin 6 (GND)")
            
    except ImportError:
        print("❌ sounddevice not available")
        print("   Install with: pip install sounddevice")
    except Exception as e:
        print(f"❌ Microphone error: {e}")
        print("   Try: arecord -D hw:2,0 -f S32_LE -r 48000 -c 2 -d 3 test.wav")

def show_wiring_guide():
    """Show the complete wiring guide"""
    print("\n📋 NUTFLIX PI 5 WIRING GUIDE")
    print("=" * 60)
    print("""
🔌 PIR Motion Sensors (AM312):
   CritterCam PIR:    VCC -> Pin 1 (3.3V)
                      GND -> Pin 6 (GND)  
                      OUT -> Pin 12 (GPIO 18)
                      
   NestCam PIR:       VCC -> Pin 17 (3.3V)
                      GND -> Pin 9 (GND)
                      OUT -> Pin 32 (GPIO 12)

🌡️  BME280 Environmental:
                      VCC -> Pin 1 (3.3V)
                      GND -> Pin 6 (GND)
                      SDA -> Pin 3 (GPIO 2)
                      SCL -> Pin 5 (GPIO 3)

💡 IR LED Controller:
                      VCC -> Pin 2 (5V)
                      GND -> Pin 6 (GND)
                      SIG -> Pin 16 (GPIO 23)

🎤 I2S Microphone (SPH0645):
                      VIN -> Pin 1 (3.3V)
                      GND -> Pin 6 (GND)
                      LRCL -> Pin 35 (GPIO 19)
                      DOUT -> Pin 38 (GPIO 20)  
                      BCLK -> Pin 40 (GPIO 21)
                      SEL -> Pin 6 (GND)
    """)

def main():
    """Main test menu"""
    print("🐿️ Nutflix Platform - Sensor Test Menu")
    print("=" * 60)
    
    while True:
        print("\nWhat would you like to test?")
        print("1. Show wiring guide")
        print("2. Test PIR motion sensors") 
        print("3. Test BME280 environmental sensor")
        print("4. Test IR LED controller")
        print("5. Test I2S microphone")
        print("6. Test all sensors")
        print("7. Exit")
        
        try:
            choice = input("\nEnter choice (1-7): ").strip()
            
            if choice == "1":
                show_wiring_guide()
            elif choice == "2":
                test_pir_sensors()
            elif choice == "3":
                test_bme280()
            elif choice == "4":
                test_ir_led()
            elif choice == "5":
                test_microphone()
            elif choice == "6":
                test_pir_sensors()
                test_bme280() 
                test_ir_led()
                test_microphone()
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
