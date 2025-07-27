#!/usr/bin/env python3
"""
I2S Microphone Interface for Adafruit SPH0645
Real I2S MEMS microphone support for Raspberry Pi 5

Pin connections:
- SEL  → GPIO 25 (Pin 22)
- LRCL → GPIO 19 (Pin 35) 
- DOUT → GPIO 13 (Pin 33)
- BCLK → GPIO 18 (Pin 12)
- GND  → Pin 20
- 3V   → Pin 17
"""

import time
import threading
import numpy as np
import subprocess
import tempfile
import os
from typing import Optional, Callable, List

class I2SMicrophone:
    def __init__(self, sample_rate: int = 44100, chunk_size: int = 1024):
        """
        Initialize I2S microphone for SPH0645
        
        Args:
            sample_rate: Audio sample rate (44100 Hz recommended)
            chunk_size: Buffer size for audio chunks
        """
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.format = 'S32_LE'  # 32-bit signed little endian for I2S
        self.channels = 1  # SPH0645 is mono
        
        # Recording state
        self.recording = False
        self.stop_event = threading.Event()
        self.record_thread = None
        self.audio_data = []
        self.callbacks = []
        
        # I2S device detection
        self.i2s_device = self._find_i2s_device()
        
    def _find_i2s_device(self) -> Optional[str]:
        """Find the I2S audio device"""
        try:
            # Check for I2S device using arecord
            result = subprocess.run(['arecord', '-l'], capture_output=True, text=True)
            lines = result.stdout.split('\n')
            
            for line in lines:
                if 'bcm2835 I2S' in line or 'I2S' in line:
                    # Extract card and device numbers
                    if 'card' in line and 'device' in line:
                        # Parse line like: "card 1: bcm2835I2S [bcm2835 I2S], device 0: bcm2835-i2s-sph0645lm4h-6 sph0645lm4h-6-0 [bcm2835-i2s-sph0645lm4h-6 sph0645lm4h-6-0]"
                        parts = line.split()
                        for i, part in enumerate(parts):
                            if part.startswith('card'):
                                card_num = part.split(':')[0].replace('card', '').strip()
                            if part.startswith('device'):
                                device_num = part.split(':')[0].replace('device', '').strip()
                        
                        device_name = f"hw:{card_num},{device_num}"
                        print(f"🎤 Found I2S device: {device_name}")
                        return device_name
            
            print("⚠️  No I2S device found - check wiring and config")
            return None
            
        except Exception as e:
            print(f"❌ Error finding I2S device: {e}")
            return None
    
    def start_recording(self, callback: Optional[Callable] = None):
        """Start continuous I2S recording"""
        if self.recording:
            print("🎤 Already recording")
            return
            
        if callback:
            self.callbacks.append(callback)
            
        self.recording = True
        self.stop_event.clear()
        self.audio_data = []
        
        if self.i2s_device:
            self._start_i2s_recording()
        else:
            self._start_mock_recording()
            
        print("🎤 I2S microphone recording started")
        
    def _start_i2s_recording(self):
        """Start real I2S recording using arecord"""
        def record_loop():
            try:
                # Use arecord to capture from I2S device
                cmd = [
                    'arecord',
                    '-D', self.i2s_device,
                    '-f', self.format,
                    '-r', str(self.sample_rate),
                    '-c', str(self.channels),
                    '--buffer-size', str(self.chunk_size * 4),  # Larger buffer for I2S
                    '-t', 'raw'  # Raw audio output
                ]
                
                print(f"🎤 Starting I2S recording: {' '.join(cmd)}")
                
                # Start arecord process
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    bufsize=0
                )
                
                bytes_per_sample = 4  # 32-bit = 4 bytes
                chunk_bytes = self.chunk_size * bytes_per_sample * self.channels
                
                while not self.stop_event.is_set():
                    try:
                        # Read chunk from arecord
                        raw_data = process.stdout.read(chunk_bytes)
                        if not raw_data:
                            break
                            
                        # Convert 32-bit to 16-bit for processing
                        audio_32 = np.frombuffer(raw_data, dtype=np.int32)
                        # Scale down from 32-bit to 16-bit range
                        audio_16 = (audio_32 >> 16).astype(np.int16)
                        
                        # Store for later retrieval
                        self.audio_data.append(audio_16)
                        
                        # Keep only last 10 seconds of audio
                        max_chunks = int(10 * self.sample_rate / self.chunk_size)
                        if len(self.audio_data) > max_chunks:
                            self.audio_data.pop(0)
                            
                        # Call callbacks with new audio data
                        for callback in self.callbacks:
                            try:
                                callback(audio_16, self.sample_rate)
                            except Exception as e:
                                print(f"❌ Audio callback error: {e}")
                                
                    except Exception as e:
                        if not self.stop_event.is_set():
                            print(f"❌ I2S read error: {e}")
                        break
                        
                # Clean up process
                process.terminate()
                process.wait()
                        
            except Exception as e:
                print(f"❌ Failed to start I2S recording: {e}")
                
        self.record_thread = threading.Thread(target=record_loop, daemon=True)
        self.record_thread.start()
        
    def _start_mock_recording(self):
        """Start mock recording for testing without I2S hardware"""
        def mock_record_loop():
            while not self.stop_event.is_set():
                # Generate mock audio data (white noise) - 16-bit format
                mock_audio = np.random.randint(-1000, 1000, self.chunk_size, dtype=np.int16)
                
                # Store mock data
                self.audio_data.append(mock_audio)
                
                # Keep only last 10 seconds
                max_chunks = int(10 * self.sample_rate / self.chunk_size)
                if len(self.audio_data) > max_chunks:
                    self.audio_data.pop(0)
                    
                # Call callbacks with mock data
                for callback in self.callbacks:
                    try:
                        callback(mock_audio, self.sample_rate)
                    except Exception as e:
                        print(f"❌ Mock callback error: {e}")
                        
                time.sleep(self.chunk_size / self.sample_rate)  # Simulate real-time
                
        self.record_thread = threading.Thread(target=mock_record_loop, daemon=True)
        self.record_thread.start()
        
    def stop_recording(self):
        """Stop I2S recording"""
        if not self.recording:
            return
            
        self.recording = False
        self.stop_event.set()
        
        if self.record_thread:
            self.record_thread.join(timeout=2)
            
        print("🎤 I2S microphone recording stopped")
        
    def get_audio_level(self) -> float:
        """Get current audio level (0.0 to 1.0)"""
        if not self.audio_data:
            return 0.0
            
        # Get RMS of recent audio data
        recent_audio = np.concatenate(self.audio_data[-5:])  # Last ~5 chunks
        rms = np.sqrt(np.mean(recent_audio.astype(np.float64) ** 2))
        
        # Normalize to 0-1 range for I2S microphone
        # I2S mics typically have much lower noise floor
        noise_floor = 10.0  # Estimate for SPH0645
        if rms > noise_floor:
            # Scale from noise floor to reasonable max (e.g., 1000 for 16-bit)
            normalized = min((rms - noise_floor) / 1000.0, 1.0)
        else:
            normalized = 0.0
        return normalized
        
    def get_recent_audio(self, duration_seconds: float = 1.0) -> np.ndarray:
        """Get recent audio data"""
        if not self.audio_data:
            return np.array([], dtype=np.int16)
            
        # Calculate how many chunks we need
        chunks_needed = int(duration_seconds * self.sample_rate / self.chunk_size)
        chunks_available = min(chunks_needed, len(self.audio_data))
        
        if chunks_available == 0:
            return np.array([], dtype=np.int16)
            
        # Get the most recent chunks
        recent_chunks = self.audio_data[-chunks_available:]
        return np.concatenate(recent_chunks)
        
    def add_callback(self, callback: Callable):
        """Add callback for real-time audio processing"""
        if callback not in self.callbacks:
            self.callbacks.append(callback)
            
    def remove_callback(self, callback: Callable):
        """Remove callback"""
        if callback in self.callbacks:
            self.callbacks.remove(callback)
            
    def is_recording(self) -> bool:
        """Check if currently recording"""
        return self.recording

# Global I2S microphone instance
i2s_microphone = None

def get_i2s_microphone() -> I2SMicrophone:
    """Get global I2S microphone instance"""
    global i2s_microphone
    if i2s_microphone is None:
        i2s_microphone = I2SMicrophone()
    return i2s_microphone

def audio_level_callback(audio_data: np.ndarray, sample_rate: int):
    """Example callback to monitor audio levels"""
    level = np.sqrt(np.mean(audio_data.astype(np.float64) ** 2))
    if level > 20:  # Threshold for I2S microphone
        print(f"🔊 Audio detected: level {level:.1f}")

# Test function
if __name__ == "__main__":
    print("🎤 Testing SPH0645 I2S Microphone...")
    print("Pin connections:")
    print("  SEL  → GPIO 25 (Pin 22)")
    print("  LRCL → GPIO 19 (Pin 35)")
    print("  DOUT → GPIO 13 (Pin 33)")
    print("  BCLK → GPIO 18 (Pin 12)")
    print("  GND  → Pin 20")
    print("  3V   → Pin 17")
    print()
    
    mic = I2SMicrophone()
    mic.add_callback(audio_level_callback)
    
    try:
        mic.start_recording()
        
        for i in range(20):  # Test for 10 seconds
            time.sleep(0.5)
            level = mic.get_audio_level()
            raw_rms = 0.0
            if mic.audio_data:
                recent_audio = np.concatenate(mic.audio_data[-5:])
                raw_rms = np.sqrt(np.mean(recent_audio.astype(np.float64) ** 2))
            print(f"Audio level: {level:.3f} (raw RMS: {raw_rms:.1f})")
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping...")
    finally:
        mic.stop_recording()
        
    print("✅ I2S microphone test complete")
