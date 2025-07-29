#!/usr/bin/env python3
"""
Simple GPIO 24 PIR Sensor Test
Tests only the NestCam PIR sensor on GPIO 24
"""

import time
import sys
try:
    import lgpio
    print("✅ lgpio library available")
except ImportError:
    print("❌ lgpio library not available")
    sys.exit(1)

def test_gpio_24_sensor():
    """Test only GPIO 24 PIR sensor"""
    
    PIR_PIN = 24
    
    print("🔌 Testing GPIO 24 PIR Sensor (NestCam)")
    print("=" * 50)
    
    try:
        # Open GPIO chip
        chip = lgpio.gpiochip_open(0)
        print(f"✅ GPIO chip opened successfully")
        
        # Set PIR pin as input with pull-down resistor
        lgpio.gpio_claim_input(chip, PIR_PIN, lgpio.SET_PULL_DOWN)
        print(f"✅ GPIO {PIR_PIN} claimed as input with pull-down")
        
        print(f"\n📍 Testing GPIO {PIR_PIN} (NestCam PIR)")
        print("🔍 Reading GPIO state (Ctrl+C to stop):")
        print("Expected: LOW (0) = no motion, HIGH (1) = motion detected")
        print("-" * 60)
        
        # Read initial state
        initial_state = lgpio.gpio_read(chip, PIR_PIN)
        print(f"Initial GPIO {PIR_PIN} state: {initial_state}")
        
        if initial_state == -1:
            print(f"❌ Error reading GPIO {PIR_PIN} - check wiring!")
            return
        
        # Continuous reading
        last_state = initial_state
        state_changes = 0
        
        for i in range(100):  # Run for 10 seconds (100 * 0.1s)
            current_state = lgpio.gpio_read(chip, PIR_PIN)
            
            if current_state != last_state:
                state_changes += 1
                timestamp = time.strftime("%H:%M:%S", time.localtime())
                print(f"[{timestamp}] 🔄 GPIO {PIR_PIN} changed: {last_state} → {current_state}")
                
                if current_state == 1:
                    print(f"    🚨 MOTION DETECTED on GPIO {PIR_PIN}!")
                elif current_state == 0:
                    print(f"    ✅ Motion ended on GPIO {PIR_PIN}")
                    
                last_state = current_state
            
            # Print status every 2 seconds
            if i % 20 == 0:
                timestamp = time.strftime("%H:%M:%S", time.localtime())
                print(f"[{timestamp}] GPIO {PIR_PIN}: {current_state} (changes: {state_changes})")
            
            time.sleep(0.1)
        
        print(f"\n📊 Test completed:")
        print(f"   Total state changes: {state_changes}")
        print(f"   Final state: {current_state}")
        
        if state_changes == 0:
            print(f"⚠️ No state changes detected - possible issues:")
            print(f"   • Check wiring to GPIO {PIR_PIN}")
            print(f"   • Ensure PIR sensor is powered (VCC connected)")
            print(f"   • Verify sensor output pin connected to GPIO {PIR_PIN}")
            print(f"   • Try waving in front of sensor")
        else:
            print(f"✅ GPIO {PIR_PIN} sensor responding to motion!")
            
    except Exception as e:
        print(f"❌ Error during GPIO test: {e}")
        
    finally:
        try:
            lgpio.gpio_free(chip, PIR_PIN)
            lgpio.gpiochip_close(chip)
            print(f"\n🧹 GPIO cleanup completed")
        except:
            pass

if __name__ == "__main__":
    print("🚀 Testing GPIO 24 PIR sensor...")
    print("Wave your hand in front of the NestCam PIR sensor during this test")
    print("")
    
    test_gpio_24_sensor()
