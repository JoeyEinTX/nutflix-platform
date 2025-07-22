
"""
AudioRecorder: Records audio from I2S mic using sounddevice and scipy.io.wavfile.
"""

import os
import threading
import time
import numpy as np
import sounddevice as sd
from scipy.io import wavfile

class AudioRecorder:
    def __init__(self, samplerate=16000, channels=1):
        self.samplerate = samplerate
        self.channels = channels
        self.recording = False
        self.thread = None
        self.frames = []
        self.stop_event = threading.Event()
        self.filename = None

    def start_recording(self, filename: str):
        if self.recording:
            return
        self.filename = filename
        self.frames = []
        self.stop_event.clear()
        self.thread = threading.Thread(target=self._record_loop, daemon=True)
        self.recording = True
        self.thread.start()

    def stop_recording(self):
        if not self.recording:
            return
        self.stop_event.set()
        if self.thread:
            self.thread.join()
        self.recording = False
        # Save to WAV file
        if self.frames and self.filename:
            try:
                audio = np.concatenate(self.frames, axis=0)
                wavfile.write(self.filename, self.samplerate, audio)
            except Exception as e:
                print(f"[AudioRecorder] Error saving audio: {e}")
        self.frames = []
        self.filename = None

    def is_recording(self) -> bool:
        return self.recording

    def _record_loop(self):
        try:
            with sd.InputStream(samplerate=self.samplerate, channels=self.channels, dtype='int16') as stream:
                while not self.stop_event.is_set():
                    data, _ = stream.read(1024)
                    self.frames.append(data.copy())
        except Exception as e:
            print(f"[AudioRecorder] Error during recording: {e}")
            self.recording = False
