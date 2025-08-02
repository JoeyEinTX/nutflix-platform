#!/usr/bin/env python3
"""
SPH0645 Hardware Verification Test
Verify power and basic connectivity
"""

import time
import sys
import os

def check_power_consumption():
    """Check if microphone is drawing power"""
    print("⚡ Power Consumption Test")
    print("=" * 40)
    print("""
To verify the SPH0645 is receiving power:

1. Check LED indicator (if your board has one)
2. Use a multimeter to verify:
   - VIN pin shows 3.3V
   - Current draw from 3.3V rail (should be ~1-2mA)
   
3. Physical inspection:
   - Ensure all solder joints are solid
   - Check for bent or broken pins
   - Verify chip orientation is correct
    """)

def test_alternative_overlay():
    """Suggest alternative I2S overlay configuration"""
    print("\n🔧 Alternative I2S Configuration")
    print("=" * 40)
    print("""
The googlevoicehat-soundcard overlay may not be optimal.
Try these alternatives in /boot/firmware/config.txt:

OPTION 1 - Simple I2S overlay:
   dtparam=i2s=on
   dtoverlay=i2s-mmap

OPTION 2 - SPH0645 specific overlay:
   dtparam=i2s=on  
   dtoverlay=googlevoicehat-soundcard,card-name=voicehat

OPTION 3 - Manual I2S configuration:
   dtparam=i2s=on
   dtoverlay=i2s-mmap,rpi-simple-soundcard

Current configuration seems correct for hardware, but might need reboot.
    """)

def suggest_wiring_double_check():
    """Provide detailed wiring verification"""
    print("\n🔌 Wiring Double-Check")
    print("=" * 40)
    print("""
SPH0645 Pin → Raspberry Pi Pin → GPIO
────────────────────────────────────────
VIN  → Pin 1  (3.3V Power)
GND  → Pin 6  (Ground)  
SEL  → Pin 1  (3.3V - for RIGHT channel)
LRCL → Pin 35 (GPIO 19) - Word Select Clock
DOUT → Pin 38 (GPIO 20) - Data Output  
BCLK → Pin 40 (GPIO 21) - Bit Clock

⚠️  CRITICAL CHECKS:
1. SEL pin MUST be connected to determine L/R channel
2. All three clock signals (LRCL, DOUT, BCLK) are required
3. Check for reversed connections
4. Ensure no short circuits between pins

🔧 Try this step-by-step:
1. Power off Pi
2. Double-check each wire connection
3. Ensure SPH0645 chip is properly seated
4. Power on and reboot (sudo reboot)
5. Test again
    """)

def test_basic_connectivity():
    """Test basic I2S device detection"""
    print("\n🔍 I2S Device Detection")
    print("=" * 40)
    
    # Check if the device can be opened for recording
    import subprocess
    
    try:
        # Try to just open the device without recording
        cmd = ["arecord", "-D", "hw:2,0", "-f", "S32_LE", "-r", "48000", "-c", "2", "-d", "0.1", "/tmp/quick_test.wav"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0:
            print("✅ I2S device opens successfully")
            
            # Check if file was created and has reasonable size
            if os.path.exists("/tmp/quick_test.wav"):
                size = os.path.getsize("/tmp/quick_test.wav")
                print(f"✅ Recording file created: {size} bytes")
                if size > 1000:  # Should be at least a few KB for 0.1 seconds
                    print("✅ File size looks reasonable")
                else:
                    print("⚠️  File size very small - might be just header")
                os.remove("/tmp/quick_test.wav")
            else:
                print("❌ Recording file was not created")
        else:
            print(f"❌ I2S device failed to open: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("❌ Recording command timed out")
    except Exception as e:
        print(f"❌ Error testing device: {e}")

def main():
    print("🎤 SPH0645 Hardware Verification")
    print("=" * 50)
    
    check_power_consumption()
    test_basic_connectivity() 
    suggest_wiring_double_check()
    test_alternative_overlay()
    
    print("\n💡 Next Steps:")
    print("=" * 30)
    print("""
1. Verify physical connections with multimeter
2. Try a different SPH0645 module if available  
3. Consider breadboard vs direct wiring issues
4. Check if chip is damaged or counterfeit
5. Test with a known working I2S microphone

If still no success, the issue is likely:
- Hardware problem (damaged chip, bad connections)
- Wrong SPH0645 variant or counterfeit chip
- Power supply issue
    """)

if __name__ == "__main__":
    main()
