"""
StreamServer: Flask server for MJPEG camera streams and health endpoint.
"""

from flask import Flask, Response, jsonify
import cv2
import threading
import time
from core.camera.camera_manager import CameraManager

class StreamServer:
    def __init__(self, device_name: str):
        self.app = Flask(__name__)
        self.cam_mgr = CameraManager(device_name)
        self._setup_routes()

    def _gen_frames(self, camera_name):
        while True:
            try:
                frame = self.cam_mgr.get_frame(camera_name)
                ret, jpeg = cv2.imencode('.jpg', frame)
                if not ret:
                    continue
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
            except Exception as e:
                print(f"[StreamServer] Warning: Could not get frame from {camera_name}: {e}")
                time.sleep(1)

    def _setup_routes(self):
        @self.app.route('/stream/crittercam')
        def stream_crittercam():
            return Response(self._gen_frames('CritterCam'),
                            mimetype='multipart/x-mixed-replace; boundary=frame')

        @self.app.route('/stream/nestcam')
        def stream_nestcam():
            return Response(self._gen_frames('NestCam'),
                            mimetype='multipart/x-mixed-replace; boundary=frame')

        @self.app.route('/health')
        def health():
            return jsonify({"status": "ok"})

    def run(self, host='0.0.0.0', port=5000, threaded=True):
        print(f"[StreamServer] Starting Flask server on {host}:{port}")
        self.app.run(host=host, port=port, threaded=threaded)

if __name__ == "__main__":
    # Example standalone usage
    server = StreamServer('nutpod')
    server.run()
