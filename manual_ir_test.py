#!/usr/bin/env python3
"""
Manual IR LED test for immediate viewing
"""

import sys
import os

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from core.infrared.ir_transmitter import IRTransmitter
    
    print("🔦 Manual IR LED Test")
    print("=" * 30)
    
    # Initialize IR LED
    ir = IRTransmitter(gpio_pin=23)
    
    print("🟢 Turning on IR LED at 100% brightness...")
    ir.turn_on(1.0)
    
    print("✅ IR LED is now ON!")
    print("👀 You should see the IR LED glowing (visible to camera, not naked eye)")
    print("🎥 Check your camera feeds at: http://localhost:8000")
    print("📹 Look for enhanced visibility in low light areas")
    
    input("\nPress Enter to turn OFF the IR LED...")
    
    print("🔴 Turning off IR LED...")
    ir.turn_off()
    
    print("✅ IR LED is now OFF")
    print("👋 Test complete!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("💡 Make sure you run this with sudo: sudo python3 manual_ir_test.py")
