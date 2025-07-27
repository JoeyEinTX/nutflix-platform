#!/usr/bin/env python3
"""Final power supply test for SPH0645"""

import RPi.GPIO as GPIO
import time

def test_power_supply():
    """Test if 3.3V power supply is reaching the SPH0645"""
    
    print("🔋 SPH0645 Power Supply Test")
    print("This will help verify if power is reaching the microphone\n")
    
    # We can't directly measure voltage with GPIO, but we can test pull-up behavior
    # A powered device should have different pull-up characteristics than unpowered
    
    VDD_PIN = 2   # 3.3V power pin on Pi (Pin 2)
    DOUT_PIN = 21 # SPH0645 DOUT pin
    
    try:
        GPIO.setmode(GPIO.BCM)
        
        print("🔧 Test 1: Checking 3.3V rail availability")
        # This is just a reminder - we can't actually measure voltage
        print("   ⚠️  Please verify with multimeter:")
        print("   📏 Pin 1 (3.3V) to Pin 6 (GND) should read ~3.3V")
        print("   📏 SPH0645 VCC to GND should read ~3.3V")
        
        print("\n🔧 Test 2: Pull-up resistance test")
        print("   Testing DOUT pin pull-up behavior...")
        
        # Test with different pull configurations
        configs = [
            (GPIO.PUD_UP, "Pull-up"),
            (GPIO.PUD_DOWN, "Pull-down"), 
            (GPIO.PUD_OFF, "No pull")
        ]
        
        for pull_config, name in configs:
            GPIO.setup(DOUT_PIN, GPIO.IN, pull_up_down=pull_config)
            time.sleep(0.1)  # Let it settle
            
            readings = []
            for _ in range(10):
                readings.append(GPIO.input(DOUT_PIN))
                time.sleep(0.01)
                
            avg = sum(readings) / len(readings)
            print(f"   {name}: {readings} (avg: {avg:.1f})")
            
        print("\n🔧 Test 3: Continuity test simulation")
        print("   ⚠️  Please check with multimeter:")
        print("   🔌 SPH0645 VCC pin should have continuity to Pi Pin 1 (3.3V)")
        print("   🔌 SPH0645 GND pin should have continuity to Pi Pin 6 (GND)")
        print("   🔌 SPH0645 DOUT pin should have continuity to Pi GPIO 21")
        print("   🔌 SPH0645 BCLK pin should have continuity to Pi GPIO 18")
        print("   🔌 SPH0645 LRCL pin should have continuity to Pi GPIO 19")
        print("   🔌 SPH0645 SEL pin should have continuity to GND")
        
        print("\n📋 Power Analysis:")
        print("   If all continuity checks pass but device still doesn't respond:")
        print("   🔴 SPH0645 is likely defective/dead")
        print("   🔴 Internal chip failure - power reaches but doesn't function")
        print("   🔴 Recommendation: Replace with known-good SPH0645")
        
    except Exception as e:
        print(f"❌ Power test error: {e}")
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    test_power_supply()
