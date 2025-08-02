#!/usr/bin/env python3
"""
SPH0645 Microphone Wiring Verification and Test
Based on the project's documentation and working configurations
"""

import sys
import time
import subprocess
import os

def check_i2s_config():
    """Check I2S configuration in boot config"""
    print("🔧 Checking I2S Configuration")
    print("=" * 50)
    
    try:
        with open("/boot/firmware/config.txt", "r") as f:
            content = f.read()
            
        print("📄 Boot config I2S settings:")
        lines = content.split('\n')
        for line in lines:
            if 'i2s' in line.lower() or 'sph0645' in line.lower() or 'googlevoicehat' in line.lower():
                print(f"   {line}")
                
        # Check if the correct overlay is loaded
        if 'googlevoicehat-soundcard' in content:
            print("✅ Google Voice HAT soundcard overlay found")
        else:
            print("❌ Google Voice HAT soundcard overlay not found")
            print("   Add: dtoverlay=googlevoicehat-soundcard")
            
    except Exception as e:
        print(f"❌ Error reading config: {e}")

def check_gpio_states():
    """Check GPIO pin states for I2S"""
    print("\n📍 Checking I2S GPIO Pin States")
    print("=" * 50)
    
    # SPH0645 I2S pins according to project wiring
    i2s_pins = {
        19: "LRCL (Left/Right Clock)",
        20: "DOUT (Data Out)", 
        21: "BCLK (Bit Clock)"
    }
    
    try:
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM)
        
        for pin, description in i2s_pins.items():
            try:
                GPIO.setup(pin, GPIO.IN)
                state = GPIO.input(pin)
                print(f"   GPIO {pin:2d} ({description}): {'HIGH' if state else 'LOW'}")
            except Exception as e:
                print(f"   GPIO {pin:2d} ({description}): Error reading - {e}")
                
        GPIO.cleanup()
        
    except ImportError:
        print("❌ RPi.GPIO not available for pin state checking")

def check_power_connections():
    """Check power and ground connections"""
    print("\n⚡ SPH0645 Power Connection Guide")
    print("=" * 50)
    print("""
Expected wiring for SPH0645:
   VIN  -> Pin 1  (3.3V)    - Red wire
   GND  -> Pin 6  (GND)     - Black wire  
   LRCL -> Pin 35 (GPIO 19) - Word Select
   DOUT -> Pin 38 (GPIO 20) - Data Out
   BCLK -> Pin 40 (GPIO 21) - Bit Clock
   SEL  -> Pin 6  (GND)     - Channel Select (L=GND, R=3.3V)
   
⚠️  CRITICAL: SEL pin determines channel!
   - Connect SEL to GND for LEFT channel
   - Connect SEL to 3.3V for RIGHT channel
   
💡 The SPH0645 only outputs on ONE channel based on SEL pin
    """)

def test_manual_arecord():
    """Test manual arecord with different settings"""
    print("\n🎤 Manual ALSA Recording Tests")
    print("=" * 50)
    
    test_configs = [
        # (format, rate, channels, duration, description)
        ("S32_LE", 48000, 2, 2, "Standard I2S format"),
        ("S16_LE", 44100, 2, 2, "CD quality fallback"),
        ("S32_LE", 16000, 2, 2, "Lower sample rate"),
    ]
    
    for fmt, rate, channels, duration, desc in test_configs:
        print(f"\n🔧 Testing: {desc}")
        print(f"   Format: {fmt}, Rate: {rate}Hz, Channels: {channels}")
        
        output_file = f"/tmp/sph0645_test_{fmt}_{rate}.wav"
        
        cmd = [
            "arecord", 
            "-D", "hw:2,0",
            "-f", fmt,
            "-r", str(rate),
            "-c", str(channels), 
            "-d", str(duration),
            output_file
        ]
        
        try:
            print(f"   Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=duration+2)
            
            if result.returncode == 0:
                # Check file size
                size = os.path.getsize(output_file)
                print(f"   ✅ Success! File size: {size} bytes")
                
                # Quick check for non-zero data
                with open(output_file, 'rb') as f:
                    f.seek(44)  # Skip WAV header
                    sample_data = f.read(1024)  # Read first 1KB of audio
                    
                non_zero_bytes = sum(1 for b in sample_data if b != 0)
                if non_zero_bytes > 10:
                    print(f"   🔊 Audio data detected! ({non_zero_bytes} non-zero bytes)")
                else:
                    print(f"   🔇 No audio signal (only {non_zero_bytes} non-zero bytes)")
            else:
                print(f"   ❌ Failed: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print(f"   ❌ Timeout")
        except Exception as e:
            print(f"   ❌ Error: {e}")

def main():
    print("🎤 SPH0645 Microphone Diagnostic Tool")
    print("=" * 60)
    
    check_i2s_config()
    check_gpio_states() 
    check_power_connections()
    test_manual_arecord()
    
    print("\n🔍 Troubleshooting Tips:")
    print("=" * 50)
    print("""
1. ⚡ Power Issues:
   - Verify 3.3V on VIN pin
   - Verify GND connections
   - Check for loose wires

2. 📡 Channel Issues:
   - SPH0645 SEL pin determines L/R channel
   - Try connecting SEL to 3.3V instead of GND
   - Audio might be on right channel only

3. 🔧 Configuration Issues:
   - Ensure I2S overlay is loaded: dtoverlay=googlevoicehat-soundcard
   - Reboot after config changes
   - Check dmesg for I2S errors: dmesg | grep i2s

4. 🎤 Hardware Issues:
   - Try a different SPH0645 if available
   - Check for damaged pins or solder joints
   - Verify breadboard connections
    """)

if __name__ == "__main__":
    main()
