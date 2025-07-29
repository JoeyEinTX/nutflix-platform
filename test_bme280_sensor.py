#!/usr/bin/env python3
"""
BME280 Environmental Sensor Test
Tests temperature, humidity, and pressure readings
"""

import time
import logging
from utils.env_sensor import EnvSensor

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def test_bme280():
    """Test BME280 environmental sensor"""
    print("🌡️ BME280 Environmental Sensor Test")
    print("=" * 40)
    
    try:
        # Test I2C detection first
        print("1️⃣ Checking I2C bus...")
        import subprocess
        result = subprocess.run(['i2cdetect', '-y', '1'], capture_output=True, text=True)
        
        if '76' in result.stdout or '77' in result.stdout:
            addr = '0x76' if '76' in result.stdout else '0x77'
            print(f"   ✅ BME280 detected at address {addr}")
        else:
            print("   ❌ BME280 not detected on I2C bus")
            print("   💡 Check wiring: CSB→3.3V, SDO→GND, SCK→GPIO3, SDA→GPIO2")
            return
        
        # Test sensor readings
        print("\n2️⃣ Testing sensor readings...")
        sensor = EnvSensor()
        
        for i in range(5):
            data = sensor.read()
            
            print(f"   Reading {i+1}:")
            print(f"     🌡️  Temperature: {data['temperature']}°C")
            print(f"     💧 Humidity: {data['humidity']}%")
            print(f"     🔽 Pressure: {data['pressure']} hPa")
            
            # Sanity check readings
            temp_ok = -40 <= data['temperature'] <= 85
            humid_ok = 0 <= data['humidity'] <= 100
            press_ok = 300 <= data['pressure'] <= 1100
            
            if temp_ok and humid_ok and press_ok:
                print("     ✅ Readings look good!")
            else:
                print("     ⚠️  Some readings seem unusual")
            
            time.sleep(2)
        
        print("\n✅ BME280 test complete!")
        
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("💡 Run: pip install adafruit-circuitpython-bme280 adafruit-blinka")
        
    except Exception as e:
        print(f"❌ BME280 test failed: {e}")
        print("💡 Check I2C is enabled: sudo raspi-config → Interface → I2C → Enable")

if __name__ == "__main__":
    test_bme280()
