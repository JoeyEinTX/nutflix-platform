#!/usr/bin/env python3
"""
IR LED Demo Script for NutFlix Platform
Demonstrates various IR LED functions for night vision
"""

import sys
import os
import time

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.infrared.ir_transmitter import IRTransmitter

def main():
    print("🔦 NutFlix IR LED Night Vision Demo")
    print("=" * 50)
    
    # Initialize IR LED
    ir = IRTransmitter(gpio_pin=23)
    
    try:
        print("\n📋 Demo Sequence:")
        print("1. Turn on at full brightness")
        print("2. Demonstrate brightness control")
        print("3. Pulse demonstration")
        print("4. Auto night mode test")
        print("5. Turn off")
        
        input("\nPress Enter to start demo...")
        
        # Demo 1: Full brightness
        print("\n🟢 Demo 1: IR LED ON at 100% brightness")
        ir.turn_on(1.0)
        time.sleep(3)
        
        # Demo 2: Brightness control
        print("\n🔆 Demo 2: Brightness control demonstration")
        brightness_levels = [0.8, 0.6, 0.4, 0.2, 0.1, 0.5, 1.0]
        
        for brightness in brightness_levels:
            print(f"   Setting brightness to {brightness*100:.0f}%")
            ir.set_brightness(brightness)
            time.sleep(1.5)
        
        # Demo 3: Pulse
        print("\n💫 Demo 3: Pulse demonstration")
        ir.turn_off()
        time.sleep(1)
        
        for i in range(3):
            print(f"   Pulse {i+1}/3")
            ir.pulse(duration=0.8, brightness=1.0)
            time.sleep(0.5)
        
        # Demo 4: Auto mode simulation
        print("\n🌙 Demo 4: Auto night mode (5 second test)")
        ir.start_auto_night_mode(light_threshold=0.5)
        time.sleep(5)
        ir.stop_auto_night_mode()
        
        # Demo 5: Turn off
        print("\n🔴 Demo 5: Turning off IR LED")
        ir.turn_off()
        
        print("\n✅ Demo complete!")
        print("\n📊 Final Status:")
        status = ir.get_status()
        print(f"   IR LED: {'🟢 ON' if status['is_on'] else '🔴 OFF'}")
        print(f"   Brightness: {status['brightness']*100:.0f}%")
        print(f"   Auto Mode: {'🌙 Enabled' if status['auto_mode'] else '⏸️ Disabled'}")
        print(f"   GPIO Pin: {status['gpio_pin']}")
        print(f"   Hardware: {'✅ Available' if status['hardware_available'] else '❌ Mock Mode'}")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Demo interrupted by user")
        
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        
    finally:
        # Cleanup
        print("\n🧹 Cleaning up...")
        ir.cleanup()
        print("👋 Goodbye!")

if __name__ == "__main__":
    main()
