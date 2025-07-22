# utils/env_sensor.py


import logging
try:
    import board
    import busio
    import adafruit_bme280
    HW_AVAILABLE = True
except ImportError:
    HW_AVAILABLE = False

class EnvSensor:
    def __init__(self, address=0x76):
        if HW_AVAILABLE:
            try:
                i2c = busio.I2C(board.SCL, board.SDA)
                self.bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=address)
                self.bme280.sea_level_pressure = 1013.25  # adjust if needed
            except Exception as e:
                logging.error(f"BME280 initialization failed: {e}")
                self.bme280 = None
        else:
            self.bme280 = None

    def read(self):
        if not self.bme280:
            # Return mock data in dev, None in prod if not available
            return {"temperature": 22.0, "humidity": 50.0, "pressure": 1012.0} if not HW_AVAILABLE else {"temperature": None, "humidity": None, "pressure": None}
        return {
            "temperature": round(self.bme280.temperature, 1),
            "humidity": round(self.bme280.humidity, 1),
            "pressure": round(self.bme280.pressure, 1)
        }
