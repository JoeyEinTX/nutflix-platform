from flask import Blueprint, jsonify, send_file, current_app
import os
import cv2
import numpy as np
from datetime import datetime

stream_bp = Blueprint('stream', __name__)

# Module-level variables for camera manager (shared from main app)
cam_mgr = None
CAMERA_AVAILABLE = False

@stream_bp.route('/api/stream/<camera_name>/thumbnail')
def get_camera_live_thumbnail(camera_name):
    """Get live thumbnail for a specific camera"""
    try:
        # Use module-level camera manager first, then try app context
        camera_manager = cam_mgr or getattr(current_app, 'camera_manager', None)
        
        if not camera_manager:
            print(f"⚠️ No camera manager available for {camera_name}")
            return generate_placeholder_thumbnail(camera_name, "No Camera Manager"), 404
        
        # Map camera names to indices
        camera_index_map = {
            'CritterCam': 0,
            'NestCam': 1
        }
        
        camera_index = camera_index_map.get(camera_name)
        if camera_index is None:
            print(f"⚠️ Unknown camera name: {camera_name}")
            return generate_placeholder_thumbnail(camera_name, "Unknown Camera"), 404
        
        # Try to capture frame from camera
        try:
            frame = camera_manager.get_frame(camera_name)
            if frame is not None:
                # Resize frame to thumbnail size
                thumbnail_frame = cv2.resize(frame, (160, 120))
                
                # Encode as JPEG
                ret, jpeg = cv2.imencode('.jpg', thumbnail_frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                if ret:
                    from io import BytesIO
                    return send_file(
                        BytesIO(jpeg.tobytes()), 
                        mimetype='image/jpeg', 
                        as_attachment=False
                    )
            
            print(f"⚠️ Failed to capture frame from {camera_name}")
            return generate_placeholder_thumbnail(camera_name, "No Frame"), 500
            
        except Exception as e:
            print(f"❌ Error capturing frame from {camera_name}: {e}")
            return generate_placeholder_thumbnail(camera_name, "Capture Error"), 500
            
    except Exception as e:
        print(f"❌ Error in live thumbnail for {camera_name}: {e}")
        return generate_placeholder_thumbnail(camera_name, "Error"), 500

def generate_placeholder_thumbnail(camera_name, message):
    """Generate a placeholder thumbnail image"""
    try:
        # Create a 160x120 gray image
        img = np.zeros((120, 160, 3), dtype=np.uint8)
        img[:] = [64, 64, 64]  # Dark gray background
        
        # Add camera name
        cv2.putText(img, camera_name, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        
        # Add message
        cv2.putText(img, message, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (200, 200, 200), 1)
        
        # Add timestamp
        timestamp = datetime.now().strftime("%H:%M:%S")
        cv2.putText(img, timestamp, (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (150, 150, 150), 1)
        
        # Encode as JPEG
        ret, jpeg = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 85])
        if ret:
            from io import BytesIO
            return send_file(
                BytesIO(jpeg.tobytes()), 
                mimetype='image/jpeg', 
                as_attachment=False
            )
    except Exception as e:
        print(f"❌ Error generating placeholder for {camera_name}: {e}")
    
    return jsonify({'error': f'Failed to generate thumbnail for {camera_name}'}), 500

@stream_bp.route('/api/stream/<camera_name>/status')
def get_camera_status(camera_name):
    """Get status information for a specific camera"""
    try:
        # Use module-level camera manager first, then try app context
        camera_manager = cam_mgr or getattr(current_app, 'camera_manager', None)
        
        if not camera_manager:
            return jsonify({
                'camera': camera_name,
                'status': 'offline',
                'message': 'No camera manager available'
            })
        
        # Map camera names to indices
        camera_index_map = {
            'CritterCam': 0,
            'NestCam': 1
        }
        
        camera_index = camera_index_map.get(camera_name)
        if camera_index is None:
            return jsonify({
                'camera': camera_name,
                'status': 'unknown',
                'message': 'Unknown camera name'
            })
        
        # Check if camera is available
        is_available = camera_index < len(camera_manager.cameras)
        
        return jsonify({
            'camera': camera_name,
            'index': camera_index,
            'status': 'online' if is_available else 'offline',
            'available': is_available,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'camera': camera_name,
            'status': 'error',
            'message': str(e)
        }), 500
