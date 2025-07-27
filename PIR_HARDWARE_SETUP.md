# AM312 PIR Motion Sensor Hardware Setup Guide

## ✅ **Using AM312 Mini PIR Sensors**

You have **HiLetgo AM312** sensors - these are **perfect** for this project! They're actually better than HC-SR501 sensors.

### **AM312 Advantages**
- ✅ **Smaller size** (12mm x 25mm - very compact)
- ✅ **Lower power** (~10µA standby vs 65mA)  
- ✅ **3.3V compatible** (works directly with Pi GPIO)
- ✅ **No adjustment needed** (no potentiometers to tune)
- ✅ **More stable** (fewer false positives)
- ✅ **Faster response** (~2 second pulse output)

## 🔌 **AM312 Wiring Diagram**

### CritterCam PIR Sensor (GPIO 18)
```
AM312 Sensor #1       →    Raspberry Pi
─────────────────────────────────────────
VCC                   →    3.3V (Pin 1)
GND                   →    GND (Pin 6) 
OUT                   →    GPIO 18 (Pin 12)
```

### NestCam PIR Sensor (GPIO 24)
```
AM312 Sensor #2       →    Raspberry Pi
─────────────────────────────────────────
VCC                   →    3.3V (Pin 17)
GND                   →    GND (Pin 9)
OUT                   →    GPIO 24 (Pin 18)
```

## 📊 **AM312 Specifications**
- **Operating Voltage**: 2.7V - 12V (using 3.3V)
- **Standby Current**: <10µA (very low power)
- **Detection Range**: 3-5 meters
- **Detection Angle**: 100 degrees
- **Output Pulse**: HIGH for ~2 seconds when motion detected
- **Warm-up Time**: 10-30 seconds after power on

## 📍 Physical Placement

### CritterCam PIR Sensor
- **Location**: Mount near CritterCam lens
- **Direction**: Aim at the same area the camera monitors
- **Height**: Same level as camera (avoid ground-level false triggers)
- **Distance**: 1-3 feet from camera (parallel coverage area)

### NestCam PIR Sensor  
- **Location**: Mount near NestCam lens
- **Direction**: Aim at the same area the camera monitors
- **Height**: Same level as camera
- **Distance**: 1-3 feet from camera (parallel coverage area)

## ⚙️ **AM312 Behavior**

### **Output Pattern**
- **Idle**: Output LOW (0V)
- **Motion Detected**: Output HIGH (3.3V) for ~2 seconds
- **Return to Idle**: Output LOW until next motion

### **No Settings Required**
Unlike HC-SR501, AM312 has:
- ❌ **No potentiometers** to adjust
- ❌ **No jumper settings** needed
- ✅ **Fixed sensitivity** (optimized for most uses)
- ✅ **Fixed time delay** (~2 second pulse)

### **Detection Characteristics**
- **Best Range**: 2-4 meters
- **Detection Angle**: 100° cone
- **Response Time**: 150ms (very fast)
- **Re-trigger Time**: Can detect new motion immediately after pulse ends

## 🧪 Testing Your Setup

### Step 1: Test Individual Sensors
```bash
cd /home/p12146/NutFlix/nutflix-platform
python3 -c "
from core.motion.dual_pir_motion_detector import DualPIRMotionDetector
detector = DualPIRMotionDetector()
detector.test_sensors(30)  # Test for 30 seconds
"
```

### Step 2: Test with Motion Detection System
```bash
python3 devices/nutpod/main.py
# Watch for PIR motion detection messages in the logs
```

### Step 3: Verify Recording Triggers
- Wave hand in front of CritterCam PIR → Should trigger CritterCam recording
- Wave hand in front of NestCam PIR → Should trigger NestCam recording  
- Check `recordings/` folder for new video files

## 🔧 Troubleshooting

### No Motion Detection
1. **Check Wiring**: Verify VCC, GND, and GPIO connections
2. **Check Power**: PIR sensors need 5V, not 3.3V
3. **Wait for Warm-up**: PIR sensors need 10-60 seconds to stabilize after power-on
4. **Test GPIO**: Run `gpio readall` to verify GPIO pins are accessible

### False Positives
1. **Check Placement**: AM312 is less prone to false triggers than HC-SR501
2. **Avoid Heat Sources**: Keep away from direct sunlight, heaters, air vents
3. **Stable Mounting**: Ensure sensors don't move or vibrate
4. **Software Cooldown**: 3-second cooldown prevents multiple triggers (adjustable in code)

### One Sensor Not Working
1. **Check Voltage**: Verify 3.3V power (not 5V - can damage AM312)
2. **Test Wiring**: Loose connections are common with small sensors
3. **Wait for Warm-up**: Allow 30 seconds after power-on before testing
4. **Swap Sensors**: Test if it's hardware or software issue

## 📊 Expected Performance

### Detection Range
- **Distance**: 3-5 meters (fixed, no adjustment)
- **Angle**: 100 degrees
- **Response Time**: 150ms (very fast)
- **Output Duration**: 2 seconds HIGH pulse

### Power Consumption
- **Per Sensor**: ~10µA standby (extremely low)
- **Total**: ~20µA for both sensors
- **Impact**: Negligible on Pi power budget

### Reliability vs Camera Motion Detection
- ✅ **No Camera Conflicts**: PIR sensors don't compete for camera access
- ✅ **Ultra Low Power**: 650x less power than HC-SR501
- ✅ **Faster Response**: 150ms detection vs video frame analysis
- ✅ **More Stable**: Fewer false positives than HC-SR501
- ✅ **Smaller Form Factor**: Easier to mount near cameras
- ⚠️  **Fixed Settings**: No adjustment capability (usually not needed)

## 🚀 **Next Steps**

1. **✅ You Already Have Hardware**: AM312 sensors are perfect for this project
2. **Wire Sensors**: Follow the 3.3V wiring diagram above (6 wires total)
3. **Test Setup**: Run the test scripts to verify detection
4. **Mount Near Cameras**: Position sensors to cover same area as cameras
5. **Enjoy Reliable Motion Detection**: No more camera conflicts!

The AM312 sensors are actually **superior** to the HC-SR501 for this application. They're smaller, use less power, and are more stable. Once wired to 3.3V (not 5V!), the system should work immediately with better performance than vision-based motion detection.
