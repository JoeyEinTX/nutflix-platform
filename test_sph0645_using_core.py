#!/usr/bin/env python3
"""
Test SPH0645 microphone using the core audio implementation
"""

import sys
import time
import os

# Add project root to path
sys.path.insert(0, '/home/p12146/Projects/Nutflix-platform')

from core.audio.sph0645_microphone import SPH0645Microphone

def test_sph0645_direct():
    """Test SPH0645 using the project's dedicated implementation"""
    print("🎤 Testing SPH0645 using core audio implementation")
    print("=" * 60)
    
    try:
        # Create microphone instance
        mic = SPH0645Microphone()
        
        # Override the card number to match our detected device (card 2)
        mic.card = 2
        
        # Add a callback to monitor audio levels
        def audio_callback(audio_data, sample_rate):
            level = abs(audio_data).mean()
            if level > 50:  # Adjust threshold as needed
                print(f"🔊 Audio detected! Level: {level:.1f}")
        
        mic.add_callback(audio_callback)
        
        print("🎤 Starting SPH0645 recording...")
        print("💬 Make some noise to test the microphone!")
        print("📊 Audio levels will be displayed when detected")
        print("⏰ Testing for 10 seconds...")
        
        mic.start_recording()
        
        # Test for 10 seconds
        for i in range(10):
            time.sleep(1)
            level = mic.get_audio_level()
            print(f"[{i+1:2d}/10] Audio level: {level:.3f}")
            
        print("✅ SPH0645 test complete!")
        
    except Exception as e:
        print(f"❌ SPH0645 test error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            mic.stop_recording()
        except:
            pass

if __name__ == "__main__":
    test_sph0645_direct()
