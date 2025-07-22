"""
RecordingEngine: Handles video/audio recording, saving to /recordings/ with timestamped filenames.
Supports background thread, max_duration, auto_stop, and future pre_record_buffer.
"""


import os
import threading
import time
from datetime import datetime, timedelta
from core.config.config_manager import get_config, ConfigError
from core.storage.file_manager import FileManager


class RecordingEngine:
    def __init__(self, device_name: str, camera_manager, audio_recorder=None):
        self.device_name = device_name
        self.config = get_config(device_name)
        self.camera_manager = camera_manager
        self.audio_recorder = audio_recorder
        self.recording = False
        self.thread = None
        self.stop_event = threading.Event()
        self.trigger_source = None
        self.max_duration = self.config.get('max_recording_duration', 30)  # seconds
        self.auto_stop = self.config.get('auto_stop', True)
        self.pre_record_buffer = self.config.get('pre_record_buffer', 0.0)
        self.file_manager = FileManager(device_name)
        self.recordings_dir = self.file_manager.recordings_dir
        # Clean old recordings once per run using cleanup_days from config
        self.file_manager.clean_old_recordings(max_age_days=self.config.get('cleanup_days', 30))
        if self.pre_record_buffer > 0:
            print(f"[RecordingEngine] WARNING: pre_record_buffer > 0 ({self.pre_record_buffer}s) but feature is not yet implemented.")

    def start_recording(self, trigger_source: str):
        if self.recording:
            return
        self.recording = True
        self.trigger_source = trigger_source
        self.stop_event.clear()
        self.thread = threading.Thread(target=self._record_loop, daemon=True)
        self.thread.start()

    def stop_recording(self):
        if not self.recording:
            return
        self.stop_event.set()
        if self.thread:
            self.thread.join()
        self.recording = False
        self.thread = None

    def is_recording(self) -> bool:
        return self.recording

    def _record_loop(self):
        start_time = datetime.now()
        cam_name = self.config.get('enabled_cameras', ['CritterCam'])[0]
        # Use file_manager to get consistent paths
        video_path = self.file_manager.get_recording_paths(trigger_type=self.trigger_source, extension=".avi")
        audio_path = self.file_manager.get_recording_paths(trigger_type=self.trigger_source, extension=".wav")
        # Video writer setup
        import cv2
        frame = self.camera_manager.get_frame(cam_name)
        height, width = frame.shape[:2]
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(video_path, fourcc, 20.0, (width, height))
        # Audio setup (if enabled)
        audio_enabled = self.config.get('record_audio', False) and self.audio_recorder
        audio_started = False
        if audio_enabled:
            try:
                self.audio_recorder.start_recording(audio_path)
                audio_started = True
            except Exception as e:
                print(f"[RecordingEngine] Audio recording failed to start: {e}")
                audio_started = False
        try:
            while not self.stop_event.is_set():
                frame = self.camera_manager.get_frame(cam_name)
                out.write(frame)
                if self.auto_stop and (datetime.now() - start_time).total_seconds() > self.max_duration:
                    break
                time.sleep(0.05)  # ~20 FPS
        finally:
            out.release()
            if audio_enabled and audio_started:
                try:
                    self.audio_recorder.stop_recording()
                except Exception as e:
                    print(f"[RecordingEngine] Audio recording failed to stop: {e}")
            # After stopping, symlink latest and optionally clean old
            self.file_manager.create_symlink_to_latest(video_path)
            # Clean again using cleanup_days from config
            self.file_manager.clean_old_recordings(max_age_days=self.config.get('cleanup_days', 30))
