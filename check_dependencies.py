#!/usr/bin/env python3
"""
Complete dependency check for Nutflix Platform
"""

def check_all_dependencies():
    print("🔍 NUTFLIX PLATFORM - COMPLETE DEPENDENCY CHECK")
    print("=" * 60)
    
    missing = []
    working = []
    
    # Core Python packages
    try:
        import numpy
        working.append("✅ NumPy")
    except ImportError:
        missing.append("❌ NumPy - pip install numpy")
    
    try:
        import cv2
        working.append("✅ OpenCV")
    except ImportError:
        missing.append("❌ OpenCV - pip install opencv-python")
    
    try:
        import flask
        working.append("✅ Flask")
    except ImportError:
        missing.append("❌ Flask - pip install flask")
    
    try:
        import flask_cors
        working.append("✅ Flask-CORS")
    except ImportError:
        missing.append("❌ Flask-CORS - pip install flask-cors")
    
    # Hardware libraries
    try:
        import RPi.GPIO
        working.append("✅ RPi.GPIO")
    except ImportError:
        missing.append("❌ RPi.GPIO - sudo apt install python3-rpi.gpio")
    
    try:
        import gpiozero
        working.append("✅ gpiozero")
    except ImportError:
        missing.append("❌ gpiozero - pip install gpiozero")
    
    try:
        from picamera2 import Picamera2
        working.append("✅ Picamera2")
    except ImportError:
        missing.append("❌ Picamera2 - pip install picamera2")
    
    # Sensor libraries
    try:
        import board
        import adafruit_bme280
        working.append("✅ BME280 libraries")
    except ImportError:
        missing.append("❌ BME280 - pip install adafruit-circuitpython-bme280 adafruit-blinka")
    
    # Audio libraries
    try:
        import sounddevice
        working.append("✅ SoundDevice")
    except ImportError:
        missing.append("❌ SoundDevice - pip install sounddevice")
    
    try:
        import pyaudio
        working.append("✅ PyAudio")
    except ImportError:
        missing.append("❌ PyAudio - pip install pyaudio")
    
    # AI/ML libraries
    try:
        import tflite_runtime
        working.append("✅ TensorFlow Lite")
    except ImportError:
        missing.append("❌ TensorFlow Lite - pip install tflite-runtime")
    
    # Config libraries
    try:
        import yaml
        working.append("✅ PyYAML")
    except ImportError:
        missing.append("❌ PyYAML - pip install pyyaml")
    
    try:
        from dotenv import load_dotenv
        working.append("✅ Python-dotenv")
    except ImportError:
        missing.append("❌ Python-dotenv - pip install python-dotenv")
    
    # Print results
    print("\n✅ WORKING DEPENDENCIES:")
    for item in working:
        print(f"   {item}")
    
    if missing:
        print("\n❌ MISSING DEPENDENCIES:")
        for item in missing:
            print(f"   {item}")
        print(f"\n📊 Status: {len(working)} working, {len(missing)} missing")
        return False
    else:
        print(f"\n🎉 ALL DEPENDENCIES INSTALLED! ({len(working)} total)")
        return True

def check_system_services():
    print("\n🔧 SYSTEM SERVICE CHECK")
    print("=" * 40)
    
    import subprocess
    
    # Check I2C
    try:
        result = subprocess.run(['i2cdetect', '-y', '1'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ I2C enabled and working")
        else:
            print("❌ I2C not working - run: sudo raspi-config -> Interface Options -> I2C")
    except FileNotFoundError:
        print("❌ i2c-tools missing - run: sudo apt install i2c-tools")
    
    # Check camera service
    import os
    video_devices = [f"/dev/video{i}" for i in range(50) if os.path.exists(f"/dev/video{i}")]
    if video_devices:
        print(f"✅ Video devices found: {len(video_devices)}")
    else:
        print("❌ No video devices found - check camera connections")
    
    # Check GPIO access
    try:
        import gpiozero
        led = gpiozero.LED(23)  # Test pin
        led.close()
        print("✅ GPIO access working")
    except Exception as e:
        print(f"❌ GPIO access issue: {e}")

if __name__ == "__main__":
    deps_ok = check_all_dependencies()
    check_system_services()
    
    if deps_ok:
        print("\n🎯 READY TO GO!")
        print("   You can now run: python3 devices/nutpod/main.py")
        print("   Or start the dashboard: python3 dashboard/app.py")
    else:
        print("\n⚠️  INSTALL MISSING DEPENDENCIES FIRST")
        print("   Then run this script again to verify")
