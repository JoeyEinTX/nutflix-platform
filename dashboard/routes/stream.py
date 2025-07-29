from flask import Blueprint, Response, jsonify, request
import cv2
import time
import numpy as np

# Try to import the real CameraManager first, fallback if needed
try:
    from core.camera.camera_manager import CameraManager
    CAMERA_AVAILABLE = True
    print("[stream_bp] CameraManager class available")
except Exception as e:
    print(f"[stream_bp] CameraManager not available: {e}")
    CAMERA_AVAILABLE = False

stream_bp = Blueprint('stream', __name__)

# Camera manager will be shared from main app - don't initialize here
cam_mgr = None
print("[stream_bp] Waiting for camera manager to be shared from main app")

def map_frontend_to_backend_camera_name(frontend_name):
    """Map frontend camera names (camera-1, camera-2, etc.) to backend names (CritterCam, NestCam)"""
    camera_map = {
        'camera-1': 'NestCam',
        'camera-2': 'CritterCam', 
        'camera-3': 'NestCam',
        'camera-4': 'CritterCam',
        'camera-5': 'NestCam',
        'camera-6': 'CritterCam',
        # Also support direct backend names
        'nestcam': 'NestCam',
        'crittercam': 'CritterCam',
        'NestCam': 'NestCam',
        'CritterCam': 'CritterCam'
    }
    backend_name = camera_map.get(frontend_name.lower(), frontend_name)
    # Only log if it's an actual mapping (not passthrough)
    if frontend_name.lower() != backend_name.lower():
        print(f"[stream_bp] Camera name mapping: '{frontend_name}' -> '{backend_name}'")
    return backend_name

def gen_frames(camera_name):
    """Generate camera frames for streaming"""
    if not CAMERA_AVAILABLE or not cam_mgr:
        # Return error frame if no camera available
        while True:
            error_frame = create_error_frame(f"Camera {camera_name} not available")
            ret, jpeg = cv2.imencode('.jpg', error_frame)
            if ret:
                yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
            time.sleep(1)
        return
        
    while True:
        try:
            frame = cam_mgr.get_frame(camera_name)
            if frame is not None:
                ret, jpeg = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                if ret:
                    yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
        except Exception as e:
            print(f"[stream_bp] Error getting frame from {camera_name}: {e}")
            # Create error frame
            error_frame = create_error_frame(f"Error: {camera_name}")
            ret, jpeg = cv2.imencode('.jpg', error_frame)
            if ret:
                yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
        time.sleep(1/30)  # 30 FPS

def create_error_frame(message):
    """Create an error frame when camera is not available"""
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    frame[:] = [40, 40, 40]  # Dark gray background
    
    # Add error message
    cv2.putText(frame, "CAMERA OFFLINE", (200, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    cv2.putText(frame, message, (150, 250), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(frame, "Check camera connection", (160, 300), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    
    return frame

@stream_bp.route('/crittercam')
def stream_crittercam():
    return Response(gen_frames('CritterCam'), mimetype='multipart/x-mixed-replace; boundary=frame')

@stream_bp.route('/nestcam')
def stream_nestcam():
    return Response(gen_frames('NestCam'), mimetype='multipart/x-mixed-replace; boundary=frame')

@stream_bp.route('/api/stream/status')
def stream_status():
    """Get stream status for both cameras"""
    cameras = {}
    
    if CAMERA_AVAILABLE and cam_mgr:
        # Get real camera status
        for camera_name in ['CritterCam', 'NestCam']:
            try:
                frame = cam_mgr.get_frame(camera_name)
                cameras[camera_name] = {
                    'active': True,
                    'url': f'/stream/{camera_name.lower()}',
                    'snapshot_url': f'/api/stream/{camera_name}/snapshot',
                    'thumbnail_url': f'/api/stream/{camera_name}/thumbnail',
                    'resolution': f'{frame.shape[1]}x{frame.shape[0]}' if frame is not None else '640x480',
                    'fps': 30,
                    'last_frame': time.time()
                }
            except Exception as e:
                print(f"[stream_bp] Camera {camera_name} not available: {e}")
                cameras[camera_name] = {
                    'active': False,
                    'error': str(e),
                    'url': f'/stream/{camera_name.lower()}',
                    'resolution': '640x480',
                    'fps': 0
                }
    else:
        # No cameras available
        for camera_name in ['CritterCam', 'NestCam']:
            cameras[camera_name] = {
                'active': False,
                'error': 'Camera system not initialized',
                'url': f'/stream/{camera_name.lower()}',
                'resolution': '640x480',
                'fps': 0
            }
    
    return jsonify({
        'cameras': cameras,
        'status': 'active' if any(cam.get('active', False) for cam in cameras.values()) else 'inactive',
        'camera_system_available': CAMERA_AVAILABLE
    })

@stream_bp.route('/api/stream/start', methods=['POST'])
def start_stream():
    """Start streaming for specific camera on-demand"""
    data = request.get_json()
    camera_name = data.get('camera') if data else None
    
    if camera_name:
        return jsonify({
            'status': 'started',
            'message': f'Live stream activated for {camera_name}',
            'camera': camera_name,
            'stream_url': f'/api/stream/{camera_name}/live'
        })
    else:
        return jsonify({
            'status': 'started',
            'message': 'All streams activated',
            'cameras': ['CritterCam', 'NestCam']
        })

@stream_bp.route('/api/stream/stop', methods=['POST']) 
def stop_stream():
    """Stop streaming for specific camera"""
    data = request.get_json()
    camera_name = data.get('camera') if data else None
    
    if camera_name:
        return jsonify({
            'status': 'stopped',
            'message': f'Live stream deactivated for {camera_name}',
            'camera': camera_name
        })
    else:
        return jsonify({
            'status': 'stopped',
            'message': 'All streams deactivated'
        })

@stream_bp.route('/api/stream/<camera_name>/live')
def get_live_stream(camera_name):
    """Get live MJPEG stream for specific camera"""
    # Map frontend camera name to backend camera name
    backend_camera_name = map_frontend_to_backend_camera_name(camera_name)
    return Response(gen_frames(backend_camera_name), mimetype='multipart/x-mixed-replace; boundary=frame')

@stream_bp.route('/api/stream/<camera_name>/snapshot')
def get_camera_snapshot(camera_name):
    """Get a single snapshot from camera"""
    # Map frontend camera name to backend camera name
    backend_camera_name = map_frontend_to_backend_camera_name(camera_name)
    
    if not CAMERA_AVAILABLE or not cam_mgr:
        return jsonify({'error': f'Camera system not available for {camera_name}'}), 503
        
    try:
        frame = cam_mgr.get_frame(backend_camera_name)
        if frame is not None:
            # Convert RGB to BGR for JPEG encoding since OpenCV expects BGR
            if len(frame.shape) == 3 and frame.shape[2] == 3:
                frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            else:
                frame_bgr = frame
                
            ret, jpeg = cv2.imencode('.jpg', frame_bgr, [cv2.IMWRITE_JPEG_QUALITY, 90])
            if ret:
                return Response(jpeg.tobytes(), mimetype='image/jpeg')
        else:
            return jsonify({'error': f'No frame available from {backend_camera_name}'}), 404
    except Exception as e:
        print(f"[stream_bp] Error getting snapshot from {backend_camera_name}: {e}")
        # Return error image
        error_frame = create_error_frame(f"Snapshot Error: {backend_camera_name}")
        ret, jpeg = cv2.imencode('.jpg', error_frame)
        if ret:
            return Response(jpeg.tobytes(), mimetype='image/jpeg')
    
    return jsonify({'error': f'Could not get snapshot from {backend_camera_name}'}), 500

@stream_bp.route('/api/stream/<camera_name>/thumbnail') 
def get_camera_thumbnail(camera_name):
    """Get a thumbnail (smaller) snapshot from camera"""
    # Map frontend camera name to backend camera name
    backend_camera_name = map_frontend_to_backend_camera_name(camera_name)
    
    if not CAMERA_AVAILABLE or not cam_mgr:
        return jsonify({'error': f'Camera system not available for {camera_name}'}), 503
        
    try:
        frame = cam_mgr.get_frame(backend_camera_name)
        if frame is not None:
            # Check for motion in the frame using sighting service
            try:
                from core.sighting_service import sighting_service
                sighting_service.check_motion_in_frame(backend_camera_name, frame)
            except Exception as motion_error:
                # Don't let motion detection errors break thumbnail generation
                pass
                
            # Convert RGB to BGR for OpenCV processing
            if len(frame.shape) == 3 and frame.shape[2] == 3:
                frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            else:
                frame_bgr = frame
                
            # Resize to thumbnail size (160x120)
            height, width = frame_bgr.shape[:2] 
            thumb_width = 160
            thumb_height = int(height * (thumb_width / width))
            thumbnail = cv2.resize(frame_bgr, (thumb_width, thumb_height))
            
            ret, jpeg = cv2.imencode('.jpg', thumbnail, [cv2.IMWRITE_JPEG_QUALITY, 75])
            if ret:
                return Response(jpeg.tobytes(), mimetype='image/jpeg')
        else:
            return jsonify({'error': f'No frame available from {backend_camera_name}'}), 404
    except Exception as e:
        print(f"[stream_bp] Error getting thumbnail from {backend_camera_name}: {e}")
        # Return error thumbnail
        error_frame = create_error_frame(f"Thumbnail Error: {backend_camera_name}")
        error_frame = cv2.resize(error_frame, (160, 120))
        ret, jpeg = cv2.imencode('.jpg', error_frame)
        if ret:
            return Response(jpeg.tobytes(), mimetype='image/jpeg')
    
    return jsonify({'error': f'Could not get thumbnail from {backend_camera_name}'}), 500
