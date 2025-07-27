#!/usr/bin/env python3 
"""Direct ALSA I2S microphone interface for SPH0645"""

import subprocess
import threading
import time
import numpy as np
from typing import Optional, Callable, List
import tempfile
import os
import wave

class SPH0645Microphone:
    """SPH0645 I2S MEMS Microphone using direct ALSA recording"""
    
    def __init__(self):
        self.recording = False
        self.stop_event = threading.Event()
        self.record_process = None
        self.record_thread = None
        self.callbacks: List[Callable] = []
        self.audio_data = []
        self.temp_wav_file = None
        
        # I2S device parameters 
        self.card = 3  # Google VoiceHAT sound card
        self.device = 0
        self.sample_rate = 48000
        self.channels = 2
        self.format = "S32_LE"  # 32-bit signed little endian
        self.chunk_duration = 0.1  # 100ms chunks
        self.chunk_samples = int(self.sample_rate * self.chunk_duration)
        
        print("🎤 SPH0645 I2S Microphone initialized")
        
    def start_recording(self, callback: Optional[Callable] = None):
        """Start continuous I2S recording using ALSA"""
        if self.recording:
            print("🎤 Already recording")
            return
            
        if callback:
            self.callbacks.append(callback)
        
        self.recording = True
        self.stop_event.clear()
        self.audio_data = []
        
        # Create temporary file for continuous recording
        self.temp_wav_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        self.temp_wav_file.close()
        
        self._start_alsa_recording()
        print("🎤 SPH0645 recording started")
        
    def _start_alsa_recording(self):
        """Start ALSA recording process"""
        def record_loop():
            try:
                # Build arecord command for continuous recording
                cmd = [
                    'arecord',
                    '-D', f'hw:{self.card},{self.device}',
                    '-f', self.format,
                    '-r', str(self.sample_rate), 
                    '-c', str(self.channels),
                    self.temp_wav_file.name
                ]
                
                print(f"🎤 Starting ALSA recording: {' '.join(cmd)}")
                
                # Start recording process
                self.record_process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
                # Monitor the recording and process chunks
                self._monitor_recording()
                
            except Exception as e:
                print(f"❌ Failed to start ALSA recording: {e}")
            finally:
                if self.record_process:
                    self.record_process.terminate()
                    self.record_process.wait()
                    
        self.record_thread = threading.Thread(target=record_loop, daemon=True)
        self.record_thread.start()
        
    def _monitor_recording(self):
        """Monitor the recording file and process audio chunks"""
        last_size = 0
        
        while not self.stop_event.is_set():
            try:
                # Check if recording file has grown
                if os.path.exists(self.temp_wav_file.name):
                    current_size = os.path.getsize(self.temp_wav_file.name)
                    
                    if current_size > last_size and current_size > 44:  # WAV header is 44 bytes
                        # Try to read new audio data
                        audio_chunk = self._read_latest_chunk()
                        if audio_chunk is not None and len(audio_chunk) > 0:
                            # Store for later retrieval
                            self.audio_data.append(audio_chunk)
                            
                            # Keep only last 10 seconds of audio
                            max_chunks = int(10 / self.chunk_duration)
                            if len(self.audio_data) > max_chunks:
                                self.audio_data.pop(0)
                            
                            # Call callbacks
                            for callback in self.callbacks:
                                try:
                                    callback(audio_chunk, self.sample_rate)
                                except Exception as e:
                                    print(f"❌ Audio callback error: {e}")
                        
                        last_size = current_size
                        
                time.sleep(self.chunk_duration)  # Check every chunk duration
                
            except Exception as e:
                if not self.stop_event.is_set():
                    print(f"❌ Recording monitor error: {e}")
                time.sleep(0.1)
                
    def _read_latest_chunk(self) -> Optional[np.ndarray]:
        """Read the latest chunk from the recording file"""
        try:
            with wave.open(self.temp_wav_file.name, 'rb') as wav_file:
                frames = wav_file.getnframes()
                sample_width = wav_file.getsampwidth()  # Should be 4 for 32-bit
                
                if frames < self.chunk_samples:
                    return None
                    
                # Read the last chunk
                start_frame = max(0, frames - self.chunk_samples)
                wav_file.setpos(start_frame)
                audio_data = wav_file.readframes(self.chunk_samples)
                
                if len(audio_data) == 0:
                    return None
                
                # Convert to numpy array (32-bit signed integers)
                audio_np = np.frombuffer(audio_data, dtype=np.int32)
                
                # Convert stereo to mono (take left channel - SPH0645 is on left)
                if len(audio_np) >= 2:
                    audio_np = audio_np[0::2]  # Every other sample starting from 0
                
                # Convert from 32-bit to 16-bit range for consistency
                audio_np = (audio_np / 65536).astype(np.int16)
                
                return audio_np
                
        except Exception as e:
            # File might be locked or incomplete
            return None
    
    def stop_recording(self):
        """Stop I2S recording"""
        if not self.recording:
            return
            
        self.recording = False
        self.stop_event.set()
        
        # Stop recording process
        if self.record_process:
            self.record_process.terminate()
            try:
                self.record_process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.record_process.kill()
                
        # Wait for thread to finish
        if self.record_thread:
            self.record_thread.join(timeout=2)
            
        # Clean up temp file
        if self.temp_wav_file and os.path.exists(self.temp_wav_file.name):
            try:
                os.unlink(self.temp_wav_file.name)
            except:
                pass
                
        print("🎤 SPH0645 recording stopped")
        
    def get_audio_level(self) -> float:
        """Get current audio level (0.0 to 1.0)"""
        if not self.audio_data:
            return 0.0
            
        # Get RMS of recent audio data
        recent_audio = np.concatenate(self.audio_data[-5:])  # Last ~5 chunks
        rms = np.sqrt(np.mean(recent_audio.astype(np.float64) ** 2))
        
        # Normalize to 0-1 range  
        noise_floor = 100  # Adjust based on testing
        if rms > noise_floor:
            normalized = min((rms - noise_floor) / 1000.0, 1.0)  # Scale above noise floor
        else:
            normalized = 0.0
        return normalized
        
    def add_callback(self, callback: Callable):
        """Add audio callback"""
        self.callbacks.append(callback)
        
    def remove_callback(self, callback: Callable):
        """Remove audio callback"""
        if callback in self.callbacks:
            self.callbacks.remove(callback)

def audio_level_callback(audio_data: np.ndarray, sample_rate: int):
    """Example callback to monitor audio levels"""
    level = np.sqrt(np.mean(audio_data.astype(np.float64) ** 2))
    if level > 100:  # Adjust threshold as needed
        print(f"🔊 Audio detected: level {level:.1f}")

# Test function
if __name__ == "__main__":
    print("🎤 Testing SPH0645 I2S Microphone...")
    
    mic = SPH0645Microphone()
    mic.add_callback(audio_level_callback)
    
    try:
        mic.start_recording()
        
        for i in range(20):  # Test for 20 seconds
            time.sleep(1)
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
        
    print("✅ SPH0645 microphone test complete")
