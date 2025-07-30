#!/usr/bin/env python3
"""
PIR Sensor Wiring Test Script
Tests GPIO connections for CritterCam (GPIO 18) and NestCam (GPIO 24) PIR sensors
"""

import time
import sys
try:
    import lgpio
    print("✅ lgpio library available")
except ImportError:
    print("❌ lgpio library not available")
    sys.exit(1)

def test_pir_wiring():
    """Test PIR sensor wiring and GPIO states"""
    
    # GPIO pins for PIR sensors
    CRITTERCAM_PIR_PIN = 18
    NESTCAM_PIR_PIN = 24
    
    print("🔌 PIR Sensor Wiring Test")
    print("=" * 50)
    
    try:
        # Open GPIO chip
        chip = lgpio.gpiochip_open(0)
        print(f"✅ GPIO chip opened successfully")
        
        # Set PIR pins as inputs with pull-down resistors
        lgpio.gpio_claim_input(chip, CRITTERCAM_PIR_PIN, lgpio.SET_PULL_DOWN)
        lgpio.gpio_claim_input(chip, NESTCAM_PIR_PIN, lgpio.SET_PULL_DOWN)
        print(f"✅ GPIO pins claimed as inputs with pull-down")
        
        print(f"\n📍 Testing GPIO {CRITTERCAM_PIR_PIN} (CritterCam PIR)")
        print(f"📍 Testing GPIO {NESTCAM_PIR_PIN} (NestCam PIR)")
        print("\n🔍 Reading GPIO states (Ctrl+C to stop):")
        print("Expected: LOW (0) = no motion, HIGH (1) = motion detected")
        print("-" * 60)
        
        # Continuous reading
        start_time = time.time()
        sample_count = 0
        
        while True:
            # Read GPIO states
            critter_state = lgpio.gpio_read(chip, CRITTERCAM_PIR_PIN)
            nest_state = lgpio.gpio_read(chip, NESTCAM_PIR_PIN)
            
            current_time = time.time()
            elapsed = current_time - start_time
            sample_count += 1
            
            # Print state every second
            if sample_count % 10 == 0:  # Print every 10th sample (roughly 1 second)
                timestamp = time.strftime("%H:%M:%S", time.localtime())
                print(f"[{timestamp}] CritterCam (GPIO {CRITTERCAM_PIR_PIN}): {critter_state} | "
                      f"NestCam (GPIO {NESTCAM_PIR_PIN}): {nest_state}")
                
                # Wiring diagnostics
                if critter_state == nest_state:
                    if critter_state == 0:
                        status = "✅ Both sensors LOW (normal idle state)"
                    else:
                        status = "⚠️ Both sensors HIGH (check for interference or wiring issue)"
                else:
                    status = f"🔍 Different states - CritterCam: {critter_state}, NestCam: {nest_state}"
                
                print(f"    Status: {status}")
                print("-" * 60)
            
            time.sleep(0.1)  # 100ms sampling rate
            
    except KeyboardInterrupt:
        print(f"\n\n📊 Test Summary:")
        print(f"⏱️ Test duration: {elapsed:.1f} seconds")
        print(f"📈 Samples collected: {sample_count}")
        print(f"\n🔌 Wiring Check:")
        print(f"   • CritterCam (GPIO 18): {'✅ Connected' if critter_state is not None else '❌ Not responding'}")
        print(f"   • NestCam (GPIO 24): {'✅ Connected' if nest_state is not None else '❌ Not responding'}")
        
        # Final state analysis
        final_critter = lgpio.gpio_read(chip, CRITTERCAM_PIR_PIN)
        final_nest = lgpio.gpio_read(chip, NESTCAM_PIR_PIN)
        
        print(f"\n🔍 Final GPIO States:")
        print(f"   • CritterCam: {final_critter} ({'LOW - No motion' if final_critter == 0 else 'HIGH - Motion detected'})")
        print(f"   • NestCam: {final_nest} ({'LOW - No motion' if final_nest == 0 else 'HIGH - Motion detected'})")
        
        if final_nest == 1:
            print(f"\n⚠️ NestCam sensor stuck HIGH - possible issues:")
            print(f"   • Loose wiring connection")
            print(f"   • Sensor in constant motion detection mode")
            print(f"   • Environmental interference (heat, air movement)")
            print(f"   • Faulty AM312 sensor")
        
    except Exception as e:
        print(f"❌ Error during GPIO test: {e}")
        
    finally:
        try:
            # Clean up GPIO
            lgpio.gpio_free(chip, CRITTERCAM_PIR_PIN)
            lgpio.gpio_free(chip, NESTCAM_PIR_PIN)
            lgpio.gpiochip_close(chip)
            print(f"\n🧹 GPIO cleanup completed")
        except:
            pass

if __name__ == "__main__":
    print("🚀 Starting PIR sensor wiring test...")
    print("This will test the direct GPIO connections for both PIR sensors")
    print("Make sure the main NutFlix system is stopped to avoid GPIO conflicts")
    print("")
    
    test_pir_wiring()
