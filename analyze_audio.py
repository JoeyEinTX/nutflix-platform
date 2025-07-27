#!/usr/bin/env python3
"""Analyze raw I2S audio data from SPH0645"""

import wave
import numpy as np
import sys

def analyze_wav_file(filename):
    """Analyze the content of a WAV file"""
    try:
        with wave.open(filename, 'rb') as wav_file:
            print(f"📁 File: {filename}")
            print(f"   Channels: {wav_file.getnchannels()}")
            print(f"   Sample Width: {wav_file.getsampwidth()} bytes")
            print(f"   Frame Rate: {wav_file.getframerate()} Hz")
            print(f"   Frames: {wav_file.getnframes()}")
            
            # Read first 1000 frames to analyze
            frames_to_read = min(1000, wav_file.getnframes())
            audio_data = wav_file.readframes(frames_to_read)
            
            # Convert to numpy array based on sample width
            if wav_file.getsampwidth() == 4:  # 32-bit
                audio_np = np.frombuffer(audio_data, dtype=np.int32)
                print(f"   Data type: 32-bit signed integer")
            elif wav_file.getsampwidth() == 2:  # 16-bit
                audio_np = np.frombuffer(audio_data, dtype=np.int16)
                print(f"   Data type: 16-bit signed integer")
            else:
                print(f"   ❌ Unsupported sample width: {wav_file.getsampwidth()}")
                return
                
            print(f"   Total samples: {len(audio_np)}")
            
            # Analyze the data
            print(f"\n📊 Raw Data Analysis:")
            print(f"   Min value: {np.min(audio_np)}")
            print(f"   Max value: {np.max(audio_np)}")
            print(f"   Mean: {np.mean(audio_np):.2f}")
            print(f"   RMS: {np.sqrt(np.mean(audio_np.astype(np.float64) ** 2)):.2f}")
            print(f"   Non-zero samples: {np.count_nonzero(audio_np)}")
            print(f"   Zero samples: {np.sum(audio_np == 0)}")
            
            # Show first 20 samples
            print(f"\n🔍 First 20 samples:")
            for i in range(min(20, len(audio_np))):
                print(f"   Sample {i}: {audio_np[i]}")
                
            # If stereo, analyze channels separately
            if wav_file.getnchannels() == 2 and len(audio_np) >= 2:
                left_channel = audio_np[0::2]
                right_channel = audio_np[1::2]
                
                print(f"\n🎧 Channel Analysis:")
                print(f"   Left channel RMS: {np.sqrt(np.mean(left_channel.astype(np.float64) ** 2)):.2f}")
                print(f"   Right channel RMS: {np.sqrt(np.mean(right_channel.astype(np.float64) ** 2)):.2f}")
                print(f"   Left non-zero: {np.count_nonzero(left_channel)}")
                print(f"   Right non-zero: {np.count_nonzero(right_channel)}")
                
    except Exception as e:
        print(f"❌ Error analyzing file: {e}")

if __name__ == "__main__":
    # Analyze the test files
    import glob
    wav_files = glob.glob("/tmp/test_*.wav")
    if wav_files:
        for wav_file in wav_files[:3]:  # Analyze up to 3 files
            analyze_wav_file(wav_file)
            print("-" * 50)
    else:
        print("No test WAV files found")
