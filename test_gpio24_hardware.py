#!/usr/bin/env python3
"""
GPIO 24 Hardware Verification Test
Checks if GPIO 24 has any hardware conflicts or special requirements
"""

import time
import sys
try:
    import lgpio
    print("✅ lgpio library available")
except ImportError:
    print("❌ lgpio library not available")
    sys.exit(1)

def test_gpio_24_hardware():
    """Test GPIO 24 hardware availability and conflicts"""
    
    PIR_PIN_24 = 24
    PIR_PIN_18 = 18  # Working sensor for comparison
    
    print("🔌 GPIO 24 Hardware Verification")
    print("=" * 50)
    
    try:
        # Open GPIO chip
        chip = lgpio.gpiochip_open(0)
        print(f"✅ GPIO chip opened successfully")
        
        # Test both pins
        print(f"\n📍 Testing GPIO availability:")
        
        # Test GPIO 18 (known working)
        try:
            lgpio.gpio_claim_input(chip, PIR_PIN_18, lgpio.SET_PULL_DOWN)
            state_18 = lgpio.gpio_read(chip, PIR_PIN_18)
            print(f"✅ GPIO {PIR_PIN_18}: Available, state = {state_18}")
            lgpio.gpio_free(chip, PIR_PIN_18)
        except Exception as e:
            print(f"❌ GPIO {PIR_PIN_18}: Error - {e}")
        
        # Test GPIO 24 (problematic)
        try:
            lgpio.gpio_claim_input(chip, PIR_PIN_24, lgpio.SET_PULL_DOWN)
            state_24 = lgpio.gpio_read(chip, PIR_PIN_24)
            print(f"✅ GPIO {PIR_PIN_24}: Available, state = {state_24}")
            
            # Try different pull resistor settings
            lgpio.gpio_free(chip, PIR_PIN_24)
            
            print(f"\n🔧 Testing different pull resistor configurations on GPIO {PIR_PIN_24}:")
            
            # Test with pull-up
            lgpio.gpio_claim_input(chip, PIR_PIN_24, lgpio.SET_PULL_UP)
            state_up = lgpio.gpio_read(chip, PIR_PIN_24)
            print(f"   Pull-UP:   {state_up}")
            lgpio.gpio_free(chip, PIR_PIN_24)
            
            # Test with no pull resistor
            lgpio.gpio_claim_input(chip, PIR_PIN_24, lgpio.SET_PULL_NONE)
            state_none = lgpio.gpio_read(chip, PIR_PIN_24)
            print(f"   Pull-NONE: {state_none}")
            lgpio.gpio_free(chip, PIR_PIN_24)
            
            # Test with pull-down (original)
            lgpio.gpio_claim_input(chip, PIR_PIN_24, lgpio.SET_PULL_DOWN)
            state_down = lgpio.gpio_read(chip, PIR_PIN_24)
            print(f"   Pull-DOWN: {state_down}")
            
            if state_up == state_down == state_none:
                print(f"⚠️ GPIO {PIR_PIN_24} shows same state ({state_up}) regardless of pull resistor")
                print(f"   This suggests:")
                print(f"   • Sensor output is strongly driving the pin")
                print(f"   • Wiring short circuit")
                print(f"   • Faulty PIR sensor")
            
        except Exception as e:
            print(f"❌ GPIO {PIR_PIN_24}: Error - {e}")
            return
        
        # Quick toggle test
        print(f"\n🔄 Manual toggle test on GPIO {PIR_PIN_24}:")
        print("   Manually connecting/disconnecting GPIO 24 to 3.3V should show state changes")
        
        for i in range(10):
            current_state = lgpio.gpio_read(chip, PIR_PIN_24)
            print(f"   Read {i+1}: {current_state}")
            time.sleep(0.5)
            
    except Exception as e:
        print(f"❌ Error during hardware test: {e}")
        
    finally:
        try:
            lgpio.gpio_free(chip, PIR_PIN_24)
            lgpio.gpiochip_close(chip)
            print(f"\n🧹 GPIO cleanup completed")
        except:
            pass

def check_gpio_conflicts():
    """Check for known GPIO 24 conflicts on Raspberry Pi"""
    print(f"\n📋 GPIO 24 Conflict Check:")
    print("=" * 30)
    
    # GPIO 24 is generally safe on most Pi models
    print("✅ GPIO 24 is a standard GPIO pin on Raspberry Pi")
    print("✅ No known hardware conflicts with GPIO 24")
    print("✅ Pin 18 (Physical) = GPIO 24 (BCM)")
    
    print(f"\n🔌 Physical Pin Layout:")
    print("   Physical Pin 18 (GPIO 24) - Right side, 9th pin from top")
    print("   Should be connected to PIR sensor OUTPUT pin")
    
    print(f"\n⚡ Power Requirements:")
    print("   PIR Sensor VCC: Connect to 3.3V or 5V (Pin 1 or 2)")
    print("   PIR Sensor GND: Connect to Ground (Pin 6, 9, 14, 20, 25, 30, 34, 39)")
    print("   PIR Sensor OUT: Connect to GPIO 24 (Pin 18)")

if __name__ == "__main__":
    print("🚀 Starting GPIO 24 hardware verification...")
    check_gpio_conflicts()
    test_gpio_24_hardware()
