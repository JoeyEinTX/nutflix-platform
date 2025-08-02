#!/usr/bin/env python3
"""Just test BME280 - nothing else"""

print("🌡️ BME280 Environmental Sensor Test")
print("=" * 50)

# Check I2C first
import subprocess
result = subprocess.run(['i2cdetect', '-y', '1'], capture_output=True, text=True)
print("I2C scan results:")
print(result.stdout)

if '76' in result.stdout or '77' in result.stdout:
    print("✅ BME280 detected!")
    
    try:
        import sys
        sys.path.append('/home/p12146/Projects/Nutflix-platform/.venv/lib/python3.11/site-packages')
        
        import board
        import adafruit_bme280
        
        i2c = board.I2C()
        bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)
        
        print("📊 Current readings:")
        temp = bme280.temperature
        humidity = bme280.relative_humidity
        pressure = bme280.pressure
        
        print(f"🌡️ Temperature: {temp:.1f}°C ({temp*9/5+32:.1f}°F)")
        print(f"💧 Humidity: {humidity:.1f}%")
        print(f"📈 Pressure: {pressure:.1f} hPa")
        
    except Exception as e:
        print(f"❌ Error reading BME280: {e}")
else:
    print("❌ BME280 not found")
    print("Wire: VCC->Pin1(3.3V), GND->Pin6, SDA->Pin3, SCL->Pin5")
