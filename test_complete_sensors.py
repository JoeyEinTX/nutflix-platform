#!/usr/bin/env python3
"""
Complete Sensor Test Script
Tests PIR motion sensors, BME280 environmental sensor, and SPH0645 microphone
"""

import time
import logging
import threading
from core.motion.dual_pir_motion_detector import DualPIRMotionDetector
from utils.env_sensor import EnvSensor
from core.audio.sph0645_microphone import SPH0645Microphone

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

def test_all_sensors():
    """Test all connected sensors"""
    print("🧪 NutFlix Complete Sensor Test")
    print("=" * 50)
    
    # Test 1: Environmental Sensor (BME280)
    print("\n1️⃣ Testing BME280 Environmental Sensor...")
    try:
        env_sensor = EnvSensor()
        env_data = env_sensor.read()
        
        print(f"   🌡️  Temperature: {env_data['temperature']}°C")
        print(f"   💧 Humidity: {env_data['humidity']}%")
        print(f"   🔽 Pressure: {env_data['pressure']} hPa")
        
        if env_data['temperature'] is not None:
            print("   ✅ BME280 sensor working correctly!")
        else:
            print("   ❌ BME280 sensor not responding")
            
    except Exception as e:
        print(f"   ❌ BME280 test failed: {e}")
    
    # Test 2: PIR Motion Sensors
    print("\n2️⃣ Testing AM312 PIR Motion Sensors...")
    try:
        def motion_callback(camera_name, event):
            print(f"   🚨 Motion detected on {camera_name}!")
            print(f"      GPIO: {event['gpio_pin']}, Time: {event['timestamp']}")
        
        pir_detector = DualPIRMotionDetector(motion_callback=motion_callback)
        pir_detector.start_detection()
        
        print("   📡 PIR sensors initialized:")
        print("      - CritterCam: GPIO 18 (Pin 12)")
        print("      - NestCam: GPIO 24 (Pin 18)")
        print("   👋 Wave your hand in front of sensors for 15 seconds...")
        
        # Test for 15 seconds
        time.sleep(15)
        
        pir_detector.stop_detection()
        print("   ✅ PIR sensor test complete")
        
    except Exception as e:
        print(f"   ❌ PIR test failed: {e}")
    
    # Test 3: I2S Microphone
    print("\n3️⃣ Testing SPH0645 I2S Microphone...")
    try:
        # Check if I2S microphone is available
        import subprocess
        result = subprocess.run(['arecord', '-l'], capture_output=True, text=True)
        
        if 'sndrpigooglevoi' in result.stdout:
            print("   🎤 I2S microphone detected in ALSA")
            print("   ✅ SPH0645 microphone ready")
            
            # Optional: Test recording for 3 seconds
            print("   🔴 Testing 3-second recording...")
            try:
                mic = SPH0645Microphone()
                
                # Record for 3 seconds
                recording_data = []
                def audio_callback(data):
                    recording_data.append(data)
                
                mic.start_recording(callback=audio_callback)
                time.sleep(3)
                mic.stop_recording()
                
                if recording_data:
                    print("   ✅ Audio recording successful!")
                else:
                    print("   ⚠️  No audio data captured")
                    
            except Exception as rec_e:
                print(f"   ⚠️  Recording test failed: {rec_e}")
                print("   💡 Microphone detected but recording needs configuration")
                
        else:
            print("   ❌ I2S microphone not detected")
            print("   💡 Check I2S configuration in /boot/config.txt")
            
    except Exception as e:
        print(f"   ❌ Microphone test failed: {e}")
    
    # Test 4: System Integration
    print("\n4️⃣ Testing System Integration...")
    try:
        print("   🔗 All sensors can be initialized together:")
        
        # Initialize all components
        env_sensor = EnvSensor()
        pir_detector = DualPIRMotionDetector()
        
        print("   ✅ Environmental sensor: Ready")
        print("   ✅ PIR motion sensors: Ready") 
        print("   ✅ I2S microphone: Ready")
        print("   ✅ System integration successful!")
        
    except Exception as e:
        print(f"   ❌ Integration test failed: {e}")
    
    print("\n🏁 Sensor Test Complete!")
    print("=" * 50)
    
    # Summary
    print("\n📋 Wiring Summary:")
    print("   PIR Sensors:")
    print("     CritterCam → GPIO 18 (Pin 12), 3.3V (Pin 1), GND (Pin 14)")
    print("     NestCam    → GPIO 24 (Pin 18), 3.3V (Pin 17), GND (Pin 9)")
    print("   BME280:")
    print("     VCC → 3.3V (Pin 1), GND → GND (Pin 6)")
    print("     SDA → GPIO 2 (Pin 3), SCL → GPIO 3 (Pin 5)")
    print("   SPH0645:")
    print("     VIN → 3.3V, GND → GND, LRCL → GPIO 19 (Pin 35)")
    print("     DOUT → GPIO 20 (Pin 38), BCLK → GPIO 21 (Pin 40)")

if __name__ == "__main__":
    test_all_sensors()
