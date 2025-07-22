import os
import threading
import time
import json
import logging
from core.utils.stitch_clips import stitch_video_audio

class ClipCoordinator:
    def __init__(self, clips_dir="clips"):
        self.sessions = {}  # key: (camera_name, timestamp), value: {video, audio, merged, meta}
        self.lock = threading.Lock()
        self.clips_dir = clips_dir
        os.makedirs(clips_dir, exist_ok=True)

    def start_session(self, camera_name: str):
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        key = (camera_name, timestamp)
        with self.lock:
            self.sessions[key] = {"video": None, "audio": None, "merged": None, "meta": None}
        logging.info(f"[ClipCoordinator] Started session for {camera_name} at {timestamp}")
        return key

    def on_video_complete(self, camera_name: str, video_path: str, timestamp=None):
        if not timestamp:
            timestamp = self._extract_timestamp(video_path)
        key = (camera_name, timestamp)
        with self.lock:
            if key not in self.sessions:
                self.sessions[key] = {"video": None, "audio": None, "merged": None, "meta": None}
            self.sessions[key]["video"] = video_path
        logging.info(f"[ClipCoordinator] Video complete for {camera_name} at {timestamp}: {video_path}")
        self._try_stitch(key)

    def on_audio_complete(self, camera_name: str, audio_path: str, timestamp=None):
        if not timestamp:
            timestamp = self._extract_timestamp(audio_path)
        key = (camera_name, timestamp)
        with self.lock:
            if key not in self.sessions:
                self.sessions[key] = {"video": None, "audio": None, "merged": None, "meta": None}
            self.sessions[key]["audio"] = audio_path
        logging.info(f"[ClipCoordinator] Audio complete for {camera_name} at {timestamp}: {audio_path}")
        self._try_stitch(key)

    def _try_stitch(self, key):
        with self.lock:
            session = self.sessions.get(key)
            if not session:
                return
            video = session["video"]
            audio = session["audio"]
            if video and audio:
                cam, ts = key
                merged_name = f"{cam}_{ts}_merged.mp4"
                merged_path = os.path.join(self.clips_dir, merged_name)
                success = stitch_video_audio(video, audio, merged_path, delete_originals=True)
                if success:
                    session["merged"] = merged_path
                    meta = {
                        "camera": cam,
                        "timestamp": ts,
                        "duration": self._get_duration(merged_path),
                        "merged_path": merged_path
                    }
                    meta_path = merged_path + ".json"
                    with open(meta_path, "w") as f:
                        json.dump(meta, f)
                    session["meta"] = meta_path
                    logging.info(f"[ClipCoordinator] Merged and saved: {merged_path} (meta: {meta_path})")
                else:
                    logging.error(f"[ClipCoordinator] Failed to stitch video/audio for {key}")

    def _extract_timestamp(self, path):
        # Assumes filename contains timestamp as ..._<timestamp>....
        base = os.path.basename(path)
        parts = base.split('_')
        for p in parts:
            if len(p) == 15 and p.isdigit():
                return p
        # fallback: current time
        return time.strftime('%Y%m%d_%H%M%S')

    def _get_duration(self, video_path):
        # Optionally use ffprobe or similar to get duration
        try:
            import subprocess
            cmd = [
                'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1', video_path
            ]
            out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL)
            return float(out.strip())
        except Exception:
            return None
