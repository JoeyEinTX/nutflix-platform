from flask import Blueprint, Response
import cv2
import time
from core.camera.camera_manager import CameraManager

stream_bp = Blueprint('stream', __name__)
cam_mgr = CameraManager('nutpod')  # Or make device_name dynamic

def gen_frames(camera_name):
    while True:
        try:
            frame = cam_mgr.get_frame(camera_name)
            ret, jpeg = cv2.imencode('.jpg', frame)
            if not ret:
                continue
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
        except Exception as e:
            print(f"[stream_bp] Warning: Could not get frame from {camera_name}: {e}")
            time.sleep(1)

@stream_bp.route('/crittercam')
def stream_crittercam():
    return Response(gen_frames('CritterCam'), mimetype='multipart/x-mixed-replace; boundary=frame')

@stream_bp.route('/nestcam')
def stream_nestcam():
    return Response(gen_frames('NestCam'), mimetype='multipart/x-mixed-replace; boundary=frame')
