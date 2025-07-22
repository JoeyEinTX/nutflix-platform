from pathlib import Path
from typing import Optional, List, Dict
import datetime

"""
FileManager: Handles file naming, directory management, and recording utilities for Nutflix.
"""

import os
import time
from datetime import datetime, timedelta

class FileManager:

    RECORDINGS_DIR = Path("/recordings")
    SNAPSHOTS_DIR = Path("/snapshots")  # optional, can reuse RECORDINGS_DIR

    def get_latest_snapshot(self, camera_name: str) -> Optional[Path]:
        """
        Returns the most recent snapshot image path for a given camera, or None if not found.
        Assumes filenames contain the camera name.
        """
        files = list(self.RECORDINGS_DIR.glob(f"*{camera_name}*.jpg"))  # Adjust extension as needed
        if not files:
            return None
        return max(files, key=lambda f: f.stat().st_mtime)

    def list_recent_clips(self, limit: int = 10) -> List[Dict]:
        """
        Returns a list of recent clips with metadata parsed from filenames.
        Expected filename format: <timestamp>_<camera>_<trigger>.mp4
        """
        clips = []
        for file in sorted(self.RECORDINGS_DIR.glob("*.mp4"), key=os.path.getmtime, reverse=True)[:limit]:
            parts = file.stem.split("_")
            if len(parts) >= 3:
                ts_str, camera, trigger = parts[0], parts[1], parts[2]
                try:
                    ts = datetime.datetime.strptime(ts_str, "%Y%m%d%H%M%S")
                except ValueError:
                    continue
                clips.append({
                    "filename": file.name,
                    "timestamp": ts,
                    "camera": camera,
                    "trigger": trigger
                })
        return clips
    def __init__(self, device_name: str, recordings_dir: str = None):
        self.device_name = device_name
        self.recordings_dir = recordings_dir or os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'recordings')
        os.makedirs(self.recordings_dir, exist_ok=True)

    def get_recording_paths(self, trigger_type: str, extension: str = ".mp4") -> str:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{self.device_name}_{trigger_type}_{timestamp}{extension}"
        return os.path.join(self.recordings_dir, filename)

    def clean_old_recordings(self, max_age_days: int):
        now = time.time()
        cutoff = now - (max_age_days * 86400)
        for fname in os.listdir(self.recordings_dir):
            fpath = os.path.join(self.recordings_dir, fname)
            if os.path.isfile(fpath):
                if os.path.getmtime(fpath) < cutoff:
                    try:
                        os.remove(fpath)
                        print(f"[FileManager] Deleted old recording: {fpath}")
                    except Exception as e:
                        print(f"[FileManager] Error deleting {fpath}: {e}")
        # TODO: Use config cleanup_days everywhere this is called for consistency

    def get_latest_clip(self) -> str:
        files = [os.path.join(self.recordings_dir, f) for f in os.listdir(self.recordings_dir) if os.path.isfile(os.path.join(self.recordings_dir, f))]
        if not files:
            return None
        latest = max(files, key=os.path.getmtime)
        return latest

    def create_symlink_to_latest(self, path: str):
        symlink_path = os.path.join(self.recordings_dir, 'latest_clip')
        try:
            if os.path.islink(symlink_path) or os.path.exists(symlink_path):
                os.remove(symlink_path)
            os.symlink(path, symlink_path)
            print(f"[FileManager] Created symlink to latest: {symlink_path} -> {path}")
        except Exception as e:
            print(f"[FileManager] Error creating symlink: {e}")

    # Future: add metadata tagging, clip categorization, etc.
