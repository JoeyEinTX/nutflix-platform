"""
I2S Microphone Integration for SPH0645
Handles recording from SPH0645 I2S microphone on Raspberry Pi 5
"""

import time
import threading
import numpy as np
from typing import Optional, Callable
import logging

# Try to import I2S-specific libraries
try:
    import pyaudio
    I2S_AVAILABLE = True
except ImportError:
    I2S_AVAILABLE = False
    print("⚠️ PyAudio not available - using mock I2S interface")

class I2SMicrophone:
    def __init__(self, sample_rate: int = 44100, channels: int = 1, chunk_size: int = 1024):
        """
        Initialize I2S microphone for SPH0645
        
        Args:
            sample_rate: Audio sample rate (44.1kHz for USB audio)
            channels: Number of channels (1 for mono, 2 for stereo)
            chunk_size: Buffer size for audio chunks
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.recording = False
        self.audio_stream = None
        self.audio_data = []
        self.callbacks = []
        
        # Threading
        self.record_thread = None
        self.stop_event = threading.Event()
        self.sample_count = 0  # Track samples to ignore initial spike
        
        # Audio format settings for USB/I2S
        self.format = pyaudio.paInt16 if I2S_AVAILABLE else None  # 16-bit is more common for USB audio
        self.input_device_index = None
        
        if I2S_AVAILABLE:
            self._find_i2s_device()
        else:
            print("🎤 I2S Microphone initialized in mock mode")
            
    def _find_i2s_device(self):
        """Find I2S or USB audio input device"""
        try:
            p = pyaudio.PyAudio()
            
            # Look specifically for the I2S device (SPH0645) first
            for i in range(p.get_device_count()):
                info = p.get_device_info_by_index(i)
                if info['maxInputChannels'] > 0:  # Input device
                    device_name = info['name'].lower()
                    # Look for the Google VoiceHAT/RPi I2S device
                    if any(pattern in device_name for pattern in ['googlevoicehat', 'rpi', 'simple']):
                        self.input_device_index = i
                        self.sample_rate = 48000  # I2S standard rate
                        self.format = pyaudio.paInt32  # I2S uses 32-bit
                        self.channels = 2  # I2S is stereo (we'll use one channel)
                        print(f"🎤 Found I2S device (SPH0645): {info['name']} (index {i})")
                        break
            
            # Fallback to USB audio if I2S not found
            if self.input_device_index is None:
                for i in range(p.get_device_count()):
                    info = p.get_device_info_by_index(i)
                    if info['maxInputChannels'] > 0:  # Input device
                        if 'maono' in info['name'].lower() or 'usb audio' in info['name'].lower():
                            self.input_device_index = i
                            print(f"🎤 Found USB audio device: {info['name']} (index {i})")
                            # Use stereo for USB audio (will convert to mono if needed)
                            self.channels = min(2, info['maxInputChannels'])
                            # Use device's default sample rate
                            self.sample_rate = int(info['defaultSampleRate'])
                            break
            
            if self.input_device_index is None:
                # Use default input device as last resort
                self.input_device_index = p.get_default_input_device_info()['index']
                print(f"🎤 Using default input device (index {self.input_device_index})")
                
            p.terminate()
            
        except Exception as e:
            print(f"❌ Error finding I2S device: {e}")
            self.input_device_index = 0
            
    def start_recording(self, callback: Optional[Callable] = None):
        """Start continuous audio recording"""
        if self.recording:
            print("🎤 Already recording")
            return
            
        if callback:
            self.callbacks.append(callback)
            
        self.recording = True
        self.stop_event.clear()
        self.audio_data = []
        self.sample_count = 0  # Reset sample counter
        
        if I2S_AVAILABLE:
            self._start_real_recording()
        else:
            self._start_mock_recording()
            
        print("🎤 I2S microphone recording started")
        
    def _start_real_recording(self):
        """Start real I2S recording using PyAudio"""
        def record_loop():
            try:
                p = pyaudio.PyAudio()
                
                self.audio_stream = p.open(
                    format=self.format,
                    channels=self.channels,
                    rate=self.sample_rate,
                    input=True,
                    input_device_index=self.input_device_index,
                    frames_per_buffer=self.chunk_size
                )
                
                while not self.stop_event.is_set():
                    try:
                        # Read audio data
                        data = self.audio_stream.read(self.chunk_size, exception_on_overflow=False)
                        
                        # Convert to numpy array (handle both I2S 32-bit and USB 16-bit)
                        if self.format == pyaudio.paInt32:
                            # I2S 32-bit data
                            audio_np = np.frombuffer(data, dtype=np.int32)
                            # Convert to 16-bit range for consistent processing
                            audio_np = (audio_np / 65536).astype(np.int16)
                        else:
                            # Regular 16-bit data
                            audio_np = np.frombuffer(data, dtype=np.int16)
                        
                        # If stereo, convert to mono by averaging channels
                        if self.channels == 2 and len(audio_np) >= 2:
                            # Take left channel only (SPH0645 is on left channel)
                            audio_np = audio_np[0::2]  # Every other sample starting from 0
                        
                        # Skip first few samples (initialization noise)
                        self.sample_count += 1
                        if self.sample_count <= 3:
                            continue
                        
                        # Store for later retrieval
                        self.audio_data.append(audio_np)
                        
                        # Keep only last 10 seconds of audio
                        max_chunks = int(10 * self.sample_rate / self.chunk_size)
                        if len(self.audio_data) > max_chunks:
                            self.audio_data.pop(0)
                            
                        # Call callbacks with new audio data
                        for callback in self.callbacks:
                            try:
                                callback(audio_np, self.sample_rate)
                            except Exception as e:
                                print(f"❌ Audio callback error: {e}")
                                
                    except Exception as e:
                        if not self.stop_event.is_set():
                            print(f"❌ Audio read error: {e}")
                        break
                        
            except Exception as e:
                print(f"❌ Failed to start I2S recording: {e}")
            finally:
                if self.audio_stream:
                    self.audio_stream.stop_stream()
                    self.audio_stream.close()
                p.terminate()
                
        self.record_thread = threading.Thread(target=record_loop, daemon=True)
        self.record_thread.start()
        
    def _start_mock_recording(self):
        """Start mock recording for testing without hardware"""
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
                    
                # Call callbacks
                for callback in self.callbacks:
                    try:
                        callback(mock_audio, self.sample_rate)
                    except Exception as e:
                        print(f"❌ Mock audio callback error: {e}")
                        
                time.sleep(self.chunk_size / self.sample_rate)  # Simulate real-time
                
        self.record_thread = threading.Thread(target=mock_record_loop, daemon=True)
        self.record_thread.start()
        
    def stop_recording(self):
        """Stop audio recording"""
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
        
        # Normalize to 0-1 range (adjust for USB microphone with noise floor ~0.7)
        # Subtract noise floor and scale appropriately
        noise_floor = 0.7
        if rms > noise_floor:
            # Scale from noise floor to reasonable max (e.g., 100)
            normalized = min((rms - noise_floor) / 50.0, 1.0)  # Scale above noise floor
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
        self.callbacks.append(callback)
        
    def remove_callback(self, callback: Callable):
        """Remove audio callback"""
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
    if level > 5:  # Threshold above noise floor of ~0.7
        print(f"🔊 Audio detected: level {level:.1f}")

# Test function
if __name__ == "__main__":
    print("🎤 Testing I2S Microphone...")
    
    mic = I2SMicrophone()
    mic.add_callback(audio_level_callback)
    
    try:
        mic.start_recording()
        
        for i in range(20):  # Increase to 20 for better observation
            time.sleep(0.5)  # Check every 0.5 seconds for more responsive monitoring
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
