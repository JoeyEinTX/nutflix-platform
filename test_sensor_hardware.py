#!/usr/bin/env python3
"""
Sensor Hardware Test Script
Tests SPH0645 microphone and IR transmitter board connectivity
"""

import sys
import os
import time

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_i2c_devices():
    """Test I2C device detection"""
    print("🔍 Scanning for I2C devices...")
    
    try:
        import subprocess
        result = subprocess.run(['i2cdetect', '-y', '1'], capture_output=True, text=True)
        if result.returncode == 0:
            print("I2C scan results:")
            print(result.stdout)
            
            # Look for common addresses
            if '40' in result.stdout:
                print("✅ Found device at 0x40 (likely PCA9685 IR transmitter)")
            if '76' in result.stdout or '77' in result.stdout:
                print("✅ Found device at 0x76/0x77 (likely BME280 sensor)")
        else:
            print("❌ i2cdetect failed - make sure I2C is enabled")
            
    except FileNotFoundError:
        print("❌ i2cdetect not found - install i2c-tools: sudo apt install i2c-tools")
    except Exception as e:
        print(f"❌ I2C scan error: {e}")

def test_audio_devices():
    """Test audio device detection"""
    print("\n🎤 Scanning for audio devices...")
    
    try:
        import pyaudio
        p = pyaudio.PyAudio()
        
        print(f"Found {p.get_device_count()} audio devices:")
        
        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:  # Input device
                print(f"  {i}: {info['name']} (inputs: {info['maxInputChannels']})")
                
        p.terminate()
        
    except ImportError:
        print("❌ PyAudio not installed - install with: pip install pyaudio")
    except Exception as e:
        print(f"❌ Audio device scan error: {e}")

def test_gpio_permissions():
    """Test GPIO access permissions"""
    print("\n🔌 Testing GPIO access...")
    
    try:
        # Check if user is in gpio group
        import subprocess
        result = subprocess.run(['groups'], capture_output=True, text=True)
        groups = result.stdout.strip()
        
        if 'gpio' in groups:
            print("✅ User is in gpio group")
        else:
            print("❌ User not in gpio group - add with: sudo usermod -a -G gpio $USER")
            
        # Check if /dev/gpiomem exists
        if os.path.exists('/dev/gpiomem'):
            print("✅ /dev/gpiomem exists")
        else:
            print("❌ /dev/gpiomem not found")
            
    except Exception as e:
        print(f"❌ GPIO permission check error: {e}")

def test_i2s_microphone():
    """Test I2S microphone"""
    print("\n🎤 Testing I2S Microphone...")
    
    try:
        from core.audio.i2s_microphone import I2SMicrophone
        
        mic = I2SMicrophone()
        print(f"✅ I2S microphone initialized")
        
        # Test recording for 3 seconds
        print("🔄 Testing 3-second recording...")
        
        def audio_callback(data, sample_rate):
            level = float(abs(data).mean())
            if level > 100:  # Adjust threshold
                print(f"🔊 Audio detected! Level: {level:.0f}")
        
        mic.add_callback(audio_callback)
        mic.start_recording()
        
        time.sleep(3)
        
        final_level = mic.get_audio_level()
        print(f"📊 Final audio level: {final_level:.3f}")
        
        mic.stop_recording()
        print("✅ I2S microphone test complete")
        
    except Exception as e:
        print(f"❌ I2S microphone test failed: {e}")

def test_ir_transmitter():
    """Test IR transmitter"""
    print("\n💡 Testing IR Transmitter...")
    
    try:
        from core.infrared.ir_transmitter import IRTransmitter
        
        ir = IRTransmitter()
        status = ir.get_status()
        print(f"✅ IR transmitter initialized")
        print(f"📊 Hardware available: {status['hardware_available']}")
        
        # Test basic operations
        print("🔄 Testing IR LED control...")
        
        ir.turn_on(0.5)
        print("💡 IR LEDs should be ON at 50%")
        time.sleep(2)
        
        ir.turn_off()
        print("💡 IR LEDs should be OFF")
        time.sleep(1)
        
        # Test pulse
        print("🔄 Testing pulse (1 second)...")
        ir.pulse(duration=1.0, brightness=0.8)
        
        print("✅ IR transmitter test complete")
        
    except Exception as e:
        print(f"❌ IR transmitter test failed: {e}")

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing sensor dependencies...")
    
    dependencies = [
        ("pyaudio", "Audio recording support"),
        ("adafruit-circuitpython-pca9685", "IR transmitter control"),
        ("adafruit-blinka", "CircuitPython compatibility"),
    ]
    
    for package, description in dependencies:
        print(f"\n🔄 Installing {package} ({description})...")
        try:
            import subprocess
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'install', package
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ {package} installed successfully")
            else:
                print(f"❌ Failed to install {package}:")
                print(result.stderr)
                
        except Exception as e:
            print(f"❌ Error installing {package}: {e}")

def check_system_config():
    """Check system configuration"""
    print("🔧 Checking system configuration...")
    
    # Check if I2C is enabled
    if os.path.exists('/dev/i2c-1'):
        print("✅ I2C interface enabled")
    else:
        print("❌ I2C interface not enabled - run: sudo raspi-config")
        
    # Check if I2S is configured
    try:
        with open('/boot/firmware/config.txt', 'r') as f:
            config = f.read()
            if 'dtparam=i2s=on' in config:
                print("✅ I2S interface enabled in config.txt")
            else:
                print("⚠️ I2S not found in config.txt - may need: dtparam=i2s=on")
    except FileNotFoundError:
        print("⚠️ Could not check /boot/firmware/config.txt")
    except Exception as e:
        print(f"⚠️ Config check error: {e}")

def main():
    """Main test function"""
    print("🚀 NutFlix Sensor Hardware Test")
    print("=" * 50)
    
    # System checks
    check_system_config()
    test_gpio_permissions()
    
    # Hardware detection
    test_i2c_devices()
    test_audio_devices()
    
    print("\n" + "=" * 50)
    
    # Offer to install dependencies
    response = input("\n💡 Install sensor dependencies? (y/n): ").lower().strip()
    if response == 'y':
        install_dependencies()
        print("\n🔄 Please restart this script after installation...")
        return
    
    print("\n" + "=" * 50)
    
    # Hardware tests
    test_i2s_microphone()
    test_ir_transmitter()
    
    print("\n" + "=" * 50)
    print("🎯 Hardware test complete!")
    print("\n📝 Next steps:")
    print("1. Connect SPH0645 microphone to I2S pins (12, 35, 38)")
    print("2. Connect IR transmitter board to I2C pins (3, 5)")
    print("3. Test audio recording with: python core/audio/i2s_microphone.py")
    print("4. Test IR control with: python core/infrared/ir_transmitter.py")

if __name__ == "__main__":
    main()
