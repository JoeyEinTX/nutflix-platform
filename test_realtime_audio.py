#!/usr/bin/env python3
"""Test if we're getting real-time audio input"""

import pyaudio
import numpy as np
import time

def test_realtime_audio():
    """Test if audio input is actually real-time"""
    print("🎤 Testing Real-time Audio Input")
    print("INSTRUCTIONS:")
    print("1. Wait for 'SILENCE NOW' - be completely quiet")
    print("2. Wait for 'MAKE NOISE NOW' - clap/talk loudly")
    print("3. We'll see if the audio follows your actions")
    
    p = pyaudio.PyAudio()
    
    try:
        # Use the Maono device directly
        stream = p.open(
            format=pyaudio.paInt16,
            channels=2,
            rate=44100,
            input=True,
            input_device_index=0,  # Maono device
            frames_per_buffer=1024
        )
        
        print("\n🔇 SILENCE NOW - Be completely quiet for 5 seconds...")
        time.sleep(2)
        
        # Record during silence
        silence_levels = []
        for i in range(20):  # 20 chunks during silence
            data = stream.read(1024, exception_on_overflow=False)
            audio_np = np.frombuffer(data, dtype=np.int16)
            rms = np.sqrt(np.mean(audio_np.astype(np.float64) ** 2))
            silence_levels.append(rms)
            if i % 5 == 0:
                print(f"   Silence sample {i//5 + 1}: {rms:.1f}")
            time.sleep(0.1)
        
        print("\n🔊 MAKE NOISE NOW - Clap/talk loudly for 5 seconds...")
        time.sleep(1)
        
        # Record during noise
        noise_levels = []
        for i in range(20):  # 20 chunks during noise
            data = stream.read(1024, exception_on_overflow=False)
            audio_np = np.frombuffer(data, dtype=np.int16)
            rms = np.sqrt(np.mean(audio_np.astype(np.float64) ** 2))
            noise_levels.append(rms)
            if i % 5 == 0:
                print(f"   Noise sample {i//5 + 1}: {rms:.1f}")
            time.sleep(0.1)
        
        stream.stop_stream()
        stream.close()
        
        # Analyze results
        avg_silence = np.mean(silence_levels)
        avg_noise = np.mean(noise_levels)
        max_silence = np.max(silence_levels)
        max_noise = np.max(noise_levels)
        
        print(f"\n📊 RESULTS:")
        print(f"   Silence: avg={avg_silence:.1f}, max={max_silence:.1f}")
        print(f"   Noise:   avg={avg_noise:.1f}, max={max_noise:.1f}")
        print(f"   Ratio:   {max_noise/max_silence:.1f}x")
        
        if max_noise > max_silence * 2:
            print("✅ REAL-TIME INPUT DETECTED!")
        else:
            print("❌ NOT REAL-TIME - Same levels during silence and noise")
            
        # Check for initialization pattern
        if silence_levels[0] > silence_levels[-1] * 2:
            print("⚠️  INITIALIZATION PATTERN DETECTED in silence")
        if noise_levels[0] > noise_levels[-1] * 2:
            print("⚠️  INITIALIZATION PATTERN DETECTED in noise")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        p.terminate()

if __name__ == "__main__":
    test_realtime_audio()
