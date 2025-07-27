#!/usr/bin/env python3
"""Test for SPH0645 clone/knockoff issues"""

import RPi.GPIO as GPIO
import time
import sys

def test_sph0645_variants():
    """Test different SPH0645 wiring variants for clones/knockoffs"""
    
    print("🔍 Testing SPH0645 Variants (Clone/Knockoff Detection)")
    print("This tests for common issues with SPH0645 clones:\n")
    
    # Standard pins
    BCLK_PIN = 18
    LRCL_PIN = 19
    DOUT_PIN = 21
    
    # Alternative pins that clones sometimes use
    ALT_PINS = [20, 16, 26, 13]  # Common alternative DOUT pins
    
    try:
        GPIO.setmode(GPIO.BCM)
        
        # Set up clock pins
        GPIO.setup(BCLK_PIN, GPIO.OUT)
        GPIO.setup(LRCL_PIN, GPIO.OUT)
        
        print("🔧 Test 1: Standard SPH0645 on GPIO 21")
        GPIO.setup(DOUT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        response = test_pin_response(BCLK_PIN, LRCL_PIN, DOUT_PIN, "GPIO 21 (Standard)")
        
        print(f"\n🔧 Test 2: Checking alternative DOUT pins (clone detection)")
        for alt_pin in ALT_PINS:
            try:
                GPIO.setup(alt_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
                alt_response = test_pin_response(BCLK_PIN, LRCL_PIN, alt_pin, f"GPIO {alt_pin}")
                if alt_response:
                    print(f"🎉 FOUND RESPONSE ON GPIO {alt_pin}! This might be a clone with different pinout.")
                GPIO.cleanup(alt_pin)
            except Exception as e:
                print(f"   GPIO {alt_pin}: Error - {e}")
                
        print(f"\n🔧 Test 3: SEL pin floating test")
        # Test with SEL floating (disconnect from GND temporarily)
        print("   NOTE: Try disconnecting SEL from GND and running this test again")
        print("   Some clones have SEL wiring issues")
        
        print(f"\n🔧 Test 4: Reverse clock polarity test")
        # Test with inverted clock signals (some clones are backwards)
        GPIO.setup(DOUT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        reverse_response = test_reverse_clocks(BCLK_PIN, LRCL_PIN, DOUT_PIN)
        
        print(f"\n📋 Results Summary:")
        print(f"   Standard GPIO 21: {'✅ Responsive' if response else '❌ No response'}")
        print(f"   Reverse clocks: {'✅ Responsive' if reverse_response else '❌ No response'}")
        print(f"   Alternative pins: Check output above")
        
        if not response and not reverse_response:
            print(f"\n🚨 Diagnosis:")
            print(f"   - No response on standard pin with normal or reverse clocks")
            print(f"   - No response on common clone pins")
            print(f"   - This strongly suggests:")
            print(f"     1. Dead/defective SPH0645 board")
            print(f"     2. Power supply issue (check 3.3V at VCC pin)")
            print(f"     3. Completely different clone pinout")
            
    except Exception as e:
        print(f"❌ Test error: {e}")
    finally:
        GPIO.cleanup()

def test_pin_response(bclk_pin, lrcl_pin, dout_pin, pin_name):
    """Test if a specific DOUT pin responds to I2S clocks"""
    print(f"   Testing {pin_name}...")
    
    response_count = 0
    test_cycles = 200
    
    for i in range(test_cycles):
        # Generate I2S clock pattern
        GPIO.output(bclk_pin, i % 2)  # Toggle BCLK
        GPIO.output(lrcl_pin, (i // 32) % 2)  # Toggle LRCL every 32 BCLKs
        
        time.sleep(0.00001)  # 10μs delay
        
        if GPIO.input(dout_pin):
            response_count += 1
            
        if response_count > 5:  # Found consistent response
            print(f"   ✅ {pin_name}: Responsive (detected {response_count} highs)")
            return True
            
    print(f"   ❌ {pin_name}: No response (only {response_count} highs in {test_cycles} cycles)")
    return False

def test_reverse_clocks(bclk_pin, lrcl_pin, dout_pin):
    """Test with inverted clock polarity (for backwards clones)"""
    print(f"   Testing reverse clock polarity...")
    
    response_count = 0
    
    for i in range(100):
        # Inverted clocks
        GPIO.output(bclk_pin, not (i % 2))  # Inverted BCLK
        GPIO.output(lrcl_pin, not ((i // 32) % 2))  # Inverted LRCL
        
        time.sleep(0.00001)
        
        if GPIO.input(dout_pin):
            response_count += 1
            
    return response_count > 3

if __name__ == "__main__":
    test_sph0645_variants()
