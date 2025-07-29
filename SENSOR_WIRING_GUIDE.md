# SPH0645 I2S Microphone + BME280 Sensor Wiring Guide

## 🎤 **SPH0645 I2S Microphone Wiring**

### **I2S Pin Connections**
```
SPH0645 Pin    →    Raspberry Pi Pin
─────────────────────────────────────────
VIN            →    Pin 2 (5V) or Pin 1 (3.3V)
GND            →    Pin 6 (Ground)
LRCL (WS)      →    Pin 35 (GPIO 19) - I2S Word Select
DOUT           →    Pin 38 (GPIO 20) - I2S Data Out
BCLK           →    Pin 40 (GPIO 21) - I2S Bit Clock
SEL            →    Pin 6 (Ground) - Channel Select (Left)
```

### **I2S Configuration Notes**
- **VIN**: Can use 3.3V or 5V (3.3V recommended to match other sensors)
- **SEL**: Connect to GND for Left channel, or 3.3V for Right channel
- **I2S Pins**: Use dedicated I2S GPIO pins (19, 20, 21)

## 🌡️ **BME280 Environmental Sensor Wiring**

### **I2C Pin Connections**
```
BME280 Pin     →    Raspberry Pi Pin
─────────────────────────────────────────
VIN/VCC        →    Pin 1 (3.3V)
GND            →    Pin 6 (Ground) - shared with other sensors
SCL            →    Pin 5 (GPIO 3) - I2C Clock
SDA            →    Pin 3 (GPIO 2) - I2C Data
```

### **I2C Address**
- **Default**: 0x76 (if SDO connected to GND)
- **Alternate**: 0x77 (if SDO connected to VCC)

## 📍 **Complete Pin Layout**

```
Raspberry Pi GPIO Header (40-pin):

Pin 1  [3.3V] ● ● [5V     ] Pin 2  ← BME280 VCC, (SPH0645 VIN optional)
Pin 3  [SDA ] ● ● [5V     ] Pin 4  ← BME280 SDA
Pin 5  [SCL ] ● ● [Ground ] Pin 6  ← BME280 SCL, Shared GND
Pin 7  [    ] ● ● [       ] Pin 8
Pin 9  [GND ] ● ● [       ] Pin 10 ← NestCam PIR GND
Pin 11 [    ] ● ● [GPIO 18] Pin 12 ← CritterCam PIR OUT
Pin 13 [    ] ● ● [Ground ] Pin 14 ← CritterCam PIR GND
Pin 15 [    ] ● ● [       ] Pin 16 
Pin 17 [3.3V] ● ● [GPIO 24] Pin 18 ← NestCam PIR VCC, NestCam PIR OUT
Pin 19 [    ] ● ● [Ground ] Pin 20
...
Pin 35 [GPIO19] ● ● [GPIO16] Pin 36 ← SPH0645 LRCL (WS)
Pin 37 [    ] ● ● [GPIO20] Pin 38 ← SPH0645 DOUT
Pin 39 [GND ] ● ● [GPIO21] Pin 40 ← SPH0645 BCLK
```

## ⚙️ **System Configuration Required**

### **1. Enable I2C for BME280**
```bash
sudo raspi-config
# Interface Options → I2C → Enable
```

### **2. Enable I2S for SPH0645**
Add to `/boot/config.txt`:
```
dtparam=i2s=on
dtoverlay=googlevoicehat-soundcard
```

### **3. Install Required Packages**
```bash
pip install adafruit-circuitpython-bme280 adafruit-blinka
sudo apt-get install alsa-utils
```

## 🧪 **Testing Your Setup**

### **Test BME280 Environmental Sensor**
```bash
cd /home/p12146/NutFlix/nutflix-platform
python3 -c "
from utils.env_sensor import EnvSensor
sensor = EnvSensor()
data = sensor.read()
print(f'Temperature: {data[\"temperature\"]}°C')
print(f'Humidity: {data[\"humidity\"]}%') 
print(f'Pressure: {data[\"pressure\"]} hPa')
"
```

### **Test SPH0645 I2S Microphone**
```bash
# Test ALSA recognition
arecord -l
# Should show: card 3: sndrpigooglevoi

# Test recording
arecord -D plughw:3,0 -c 2 -r 48000 -f S32_LE -t wav -V mono -v test_mic.wav
```

### **Test PIR + Environmental Integration**
```bash
python3 devices/nutpod/main.py
# Should show:
# ✓ PIR motion detection started
# ✓ Environmental sensor initialized  
# ✓ I2S microphone ready
```

## 🔧 **Troubleshooting**

### **BME280 Issues**
- **Not detected**: Check I2C address with `i2cdetect -y 1`
- **Connection errors**: Verify 3.3V power and I2C wiring
- **Import errors**: Install `adafruit-circuitpython-bme280`

### **SPH0645 Issues**
- **No audio device**: Check I2S overlay in `/boot/config.txt`
- **Recording fails**: Verify I2S pin connections (19, 20, 21)
- **No sound**: Ensure `SEL` pin connected to GND for left channel

### **Power Considerations**
- **Total current draw**: ~50mA (very reasonable for Pi)
- **Shared 3.3V**: All sensors can share single 3.3V rail
- **Ground loops**: Use star grounding pattern from single GND pin

## 📊 **Expected Performance**

### **BME280 Environmental Sensor**
- **Temperature**: ±1°C accuracy
- **Humidity**: ±3% RH accuracy  
- **Pressure**: ±1 hPa accuracy
- **Update Rate**: 1Hz (configurable)

### **SPH0645 I2S Microphone**
- **Sample Rate**: 48kHz
- **Bit Depth**: 24-bit
- **Frequency Response**: 50Hz - 15kHz
- **SNR**: 65 dBA

Your complete sensor array will provide:
- 🚨 **Motion Detection**: AM312 PIR sensors (GPIO 18, 24)
- 🌡️ **Environmental Data**: BME280 (I2C)
- 🎤 **Audio Recording**: SPH0645 (I2S)
- 📹 **Video Recording**: Cameras with on-demand streaming

This gives you a comprehensive wildlife monitoring system with hardware-based motion triggers!
