
"""
MotionDetector: Detects motion in CritterCam frames using frame differencing.
Supports sensitivity adjustment and cooldown debounce.
"""

import numpy as np
import cv2
from datetime import datetime, timedelta

class MotionDetector:
    def __init__(self, motion_sensitivity: float = 0.4, cooldown_sec: float = 1.0):
        self.motion_sensitivity = motion_sensitivity
        self.cooldown = timedelta(seconds=cooldown_sec)
        self.last_motion_time = None
        self.last_frame = None
        self.last_detection = False
        self.last_detection_time = None

    def detect_motion(self, frame: np.ndarray) -> bool:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        motion = False
        now = datetime.now()
        if self.last_frame is not None:
            # Compute absolute difference
            frame_delta = cv2.absdiff(self.last_frame, gray)
            thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
            motion_pixels = np.sum(thresh > 0)
            total_pixels = thresh.size
            motion_ratio = motion_pixels / total_pixels
            if motion_ratio > self.motion_sensitivity:
                # Debounce: only trigger if cooldown passed
                if not self.last_detection or (now - self.last_detection_time) > self.cooldown:
                    motion = True
                    self.last_motion_time = now
                    self.last_detection_time = now
                    self.last_detection = True
            else:
                self.last_detection = False
        self.last_frame = gray
        return motion

    def get_last_motion_time(self) -> datetime:
        return self.last_motion_time
