# PIR Motion Sensor Integration for NutFlix

## Hardware Setup
- **PIR Sensor**: Connect to GPIO pin (e.g., GPIO 18)
- **Power**: 5V from Pi
- **Ground**: GND to Pi
- **Signal**: Data pin to GPIO

## Benefits Over Camera-Based Motion Detection:
1. **No Camera Conflicts**: Cameras only activate when motion detected
2. **Lower Power Consumption**: PIR vs continuous video processing
3. **Faster Response**: Instant trigger vs frame analysis
4. **More Reliable**: Works in all lighting/weather conditions

## Implementation Plan:
1. Wire PIR sensor to GPIO 18
2. Create PIRMotionDetector class
3. ✅ **COMPLETED** - Removed VisionMotionDetector from sighting_service.py
4. Test motion triggering → recording flow

## Hardware Needed:
- PIR Motion Sensor (HC-SR501 or similar) - $5-10
- Jumper wires
- Optional: weatherproof enclosure

## GPIO Wiring:
```
PIR Sensor    → Raspberry Pi
VCC (5V)      → Pin 2 (5V)
GND           → Pin 6 (Ground)  
OUT (Signal)  → Pin 12 (GPIO 18)
```

This eliminates all camera hardware conflicts while providing reliable motion detection.
