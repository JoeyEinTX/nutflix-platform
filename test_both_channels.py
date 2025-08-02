#!/usr/bin/env python3
"""
Test both audio channels to see if SPH0645 is working on right channel
"""

import subprocess
import numpy as np
import wave
import os

def test_both_channels():
    """Test both left and right channels of I2S microphone"""
    print("🎤 Testing SPH0645 Both Audio Channels")
    print("=" * 50)
    
    # Record 3 seconds of stereo audio
    output_file = "/tmp/test_both_channels_detailed.wav"
    
    print("🎵 Recording 3 seconds of audio...")
    print("💬 Make some noise now!")
    
    cmd = [
        "arecord", 
        "-D", "hw:2,0",
        "-f", "S32_LE",
        "-r", "48000",
        "-c", "2",
        "-d", "3",
        output_file
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Recording failed: {result.stderr}")
            return
            
        print("✅ Recording complete! Analyzing both channels...")
        
        # Read the WAV file and analyze both channels
        with wave.open(output_file, 'rb') as wav_file:
            frames = wav_file.getnframes()
            audio_data = wav_file.readframes(frames)
            
        # Convert to numpy array (32-bit signed integers)
        audio_np = np.frombuffer(audio_data, dtype=np.int32)
        
        # Separate left and right channels
        left_channel = audio_np[0::2]   # Every other sample starting from 0
        right_channel = audio_np[1::2]  # Every other sample starting from 1
        
        # Calculate statistics for both channels
        left_mean = abs(left_channel).mean()
        left_max = abs(left_channel).max()
        left_std = left_channel.std()
        
        right_mean = abs(right_channel).mean()
        right_max = abs(right_channel).max()
        right_std = right_channel.std()
        
        print("\n📊 Channel Analysis:")
        print("=" * 30)
        print(f"LEFT Channel (SEL=GND):")
        print(f"  Average: {left_mean:.1f}")
        print(f"  Peak:    {left_max:.1f}")
        print(f"  StdDev:  {left_std:.1f}")
        
        print(f"\nRIGHT Channel (SEL=3.3V):")
        print(f"  Average: {right_mean:.1f}")
        print(f"  Peak:    {right_max:.1f}")
        print(f"  StdDev:  {right_std:.1f}")
        
        # Determine which channel has audio
        threshold = 1000  # Adjust as needed
        
        left_active = left_mean > threshold or left_max > threshold*10
        right_active = right_mean > threshold or right_max > threshold*10
        
        print(f"\n🔍 Results:")
        if left_active:
            print("🔊 LEFT channel has audio signal!")
        else:
            print("🔇 LEFT channel is silent")
            
        if right_active:
            print("🔊 RIGHT channel has audio signal!")
        else:
            print("🔇 RIGHT channel is silent")
            
        if not left_active and not right_active:
            print("❌ No audio detected on either channel")
            print("   Possible issues:")
            print("   - Check power connections (VIN to 3.3V)")
            print("   - Check data connections (DOUT, LRCL, BCLK)")
            print("   - Try different SPH0645 module")
            print("   - Check for loose wires or bad connections")
        
        # Show sample values for debugging
        print(f"\n🔬 Sample Values (first 10):")
        print(f"LEFT:  {left_channel[:10]}")
        print(f"RIGHT: {right_channel[:10]}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if os.path.exists(output_file):
            os.remove(output_file)

if __name__ == "__main__":
    test_both_channels()
