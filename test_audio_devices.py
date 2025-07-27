#!/usr/bin/env python3
"""Test different audio input devices and channels"""

import pyaudio
import numpy as np
import time

def test_device(device_index, device_name, duration=3):
    """Test a specific audio device"""
    print(f"\n🎤 Testing Device {device_index}: {device_name}")
    
    try:
        p = pyaudio.PyAudio()
        
        # Get device info
        device_info = p.get_device_info_by_index(device_index)
        max_channels = min(device_info['maxInputChannels'], 2)  # Limit to 2 channels max
        
        if max_channels == 0:
            print("❌ No input channels available")
            p.terminate()
            return
            
        print(f"   Channels: {max_channels}, Sample Rate: {device_info['defaultSampleRate']}")
        
        # Try to open stream
        stream = p.open(
            format=pyaudio.paInt16,
            channels=max_channels,
            rate=int(device_info['defaultSampleRate']),
            input=True,
            input_device_index=device_index,
            frames_per_buffer=1024
        )
        
        print(f"   🎧 Recording for {duration} seconds... (make some noise!)")
        
        max_rms = 0.0
        samples_count = 0
        
        for i in range(int(duration * device_info['defaultSampleRate'] / 1024)):
            try:
                data = stream.read(1024, exception_on_overflow=False)
                audio_np = np.frombuffer(data, dtype=np.int16)
                
                # Calculate RMS for all channels combined
                rms_combined = np.sqrt(np.mean(audio_np.astype(np.float64) ** 2))
                max_rms = max(max_rms, rms_combined)
                
                # If stereo, also check individual channels
                if max_channels == 2 and len(audio_np) >= 2:
                    # Separate left and right channels
                    left_channel = audio_np[0::2]  # Every other sample starting from 0
                    right_channel = audio_np[1::2]  # Every other sample starting from 1
                    
                    rms_left = np.sqrt(np.mean(left_channel.astype(np.float64) ** 2))
                    rms_right = np.sqrt(np.mean(right_channel.astype(np.float64) ** 2))
                    
                    if rms_combined > 5:  # Only show when there's actual audio
                        print(f"   📊 Combined: {rms_combined:.1f}, Left: {rms_left:.1f}, Right: {rms_right:.1f}")
                
                samples_count += 1
                
            except Exception as e:
                print(f"   ❌ Read error: {e}")
                break
                
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        print(f"   ✅ Max RMS detected: {max_rms:.1f}")
        if max_rms < 1:
            print("   ⚠️  Very low audio levels - might be wrong input or no signal")
        elif max_rms > 50:
            print("   🎉 Good audio levels detected!")
        else:
            print("   📈 Some audio detected")
            
    except Exception as e:
        print(f"   ❌ Failed to test device: {e}")

if __name__ == "__main__":
    print("🔊 Testing Audio Input Devices")
    print("Make some noise (clap, talk) during each test!")
    
    # Test specific devices that are most likely to work
    devices_to_test = [
        (0, "Maono ProStudio 2x2 Lite (hw:0,0)"),
        (10, "pulse"),
        (16, "default"),
    ]
    
    for device_idx, device_name in devices_to_test:
        test_device(device_idx, device_name, duration=5)
        time.sleep(1)  # Brief pause between tests
    
    print("\n🎯 Test complete! Look for the device with highest RMS values.")
