#!/usr/bin/env python3
"""Test SPH0645 connection by checking if it responds to I2S signals"""

import RPi.GPIO as GPIO
import time
import sys

def test_sph0645_connection():
    """Test if SPH0645 is properly connected by checking signal response"""
    
    print("🔧 Testing SPH0645 Hardware Connection...")
    
    # I2S pin configuration
    BCLK_PIN = 18   # Bit clock
    LRCL_PIN = 19   # Left/Right clock  
    DOUT_PIN = 21   # Data out
    
    try:
        GPIO.setmode(GPIO.BCM)
        
        # Set up pins
        GPIO.setup(BCLK_PIN, GPIO.OUT)  # Bit clock output
        GPIO.setup(LRCL_PIN, GPIO.OUT)  # Word select output
        GPIO.setup(DOUT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # Data input
        
        print(f"📡 GPIO Configuration:")
        print(f"   BCLK (GPIO {BCLK_PIN}): Output")
        print(f"   LRCL (GPIO {LRCL_PIN}): Output") 
        print(f"   DOUT (GPIO {DOUT_PIN}): Input")
        
        # Test 1: Check if DOUT pin responds to clock signals
        print(f"\n🔍 Test 1: Checking DOUT pin response...")
        
        # Generate some clock signals
        for i in range(100):
            GPIO.output(BCLK_PIN, GPIO.HIGH)
            GPIO.output(LRCL_PIN, i % 2)  # Toggle word select
            time.sleep(0.00001)  # 10μs
            
            dout_state = GPIO.input(DOUT_PIN)
            if dout_state:
                print(f"✅ DOUT pin active (cycle {i})")
                break
                
            GPIO.output(BCLK_PIN, GPIO.LOW)
            time.sleep(0.00001)
        else:
            print("❌ DOUT pin never went high - possible connection issue")
            
        # Test 2: Check steady state behavior
        print(f"\n🔍 Test 2: Checking steady state...")
        GPIO.output(BCLK_PIN, GPIO.LOW)
        GPIO.output(LRCL_PIN, GPIO.LOW)
        time.sleep(0.1)
        
        dout_baseline = GPIO.input(DOUT_PIN)
        print(f"   DOUT baseline: {'HIGH' if dout_baseline else 'LOW'}")
        
        # Test 3: Power check (indirect)
        print(f"\n🔍 Test 3: Connection verification...")
        
        # Try different clock patterns
        patterns_detected = 0
        for pattern in range(5):
            for cycle in range(20):
                if pattern == 0:
                    # Fast clock
                    GPIO.output(BCLK_PIN, cycle % 2)
                    GPIO.output(LRCL_PIN, 0)
                elif pattern == 1:
                    # Slow clock
                    GPIO.output(BCLK_PIN, cycle % 2)
                    GPIO.output(LRCL_PIN, cycle // 10)
                else:
                    # Various patterns
                    GPIO.output(BCLK_PIN, (cycle + pattern) % 2)
                    GPIO.output(LRCL_PIN, cycle % 4 < 2)
                    
                time.sleep(0.0001)
                
                if GPIO.input(DOUT_PIN):
                    patterns_detected += 1
                    break
                    
        print(f"   Patterns with DOUT response: {patterns_detected}/5")
        
        if patterns_detected > 0:
            print("✅ SPH0645 appears to be responding to clock signals")
        else:
            print("❌ SPH0645 not responding - check wiring and power")
            
    except Exception as e:
        print(f"❌ Test error: {e}")
    finally:
        GPIO.cleanup()
        
    print("\n📋 Troubleshooting checklist:")
    print("   ✅ BCLK → GPIO 18 (Pin 12)")
    print("   ✅ LRCL → GPIO 19 (Pin 35)")  
    print("   ✅ DOUT → GPIO 21 (Pin 40)")
    print("   ✅ SEL → GND (Pin 39)")
    print("   ✅ VCC → 3.3V (Pin 17)")
    print("   ✅ GND → GND (Pin 20)")

if __name__ == "__main__":
    test_sph0645_connection()
