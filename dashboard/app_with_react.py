#!/usr/bin/env python3
"""
Nutflix Platform - API Backend
Enhanced Flask backend designed to serve as API for React frontend
"""

import sys
import os
from pathlib import Path

# Add the parent directory to Python path so we can import 'core'
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, redirect, url_for, render_template, jsonify, send_from_directory, request, Response, make_response, send_file
from flask_cors import CORS
import json
from datetime import datetime, timedelta

# Import clip manager for latest clip functionality
try:
    from core.clip_manager import ClipManager
    CLIP_MANAGER_AVAILABLE = True
    print("✅ ClipManager imported successfully")
except ImportError as e:
    print(f"❌ ClipManager not available: {e}")
    CLIP_MANAGER_AVAILABLE = False

# Import sighting service
try:
    from core.sighting_service import sighting_service
    SIGHTING_SERVICE_AVAILABLE = True
    print("✅ Sighting service imported successfully")
except ImportError as e:
    print(f"❌ Sighting service not available: {e}")
    SIGHTING_SERVICE_AVAILABLE = False

# Import PIR motion detector
try:
    from core.motion.dual_pir_motion_detector import DualPIRMotionDetector
    PIR_DETECTOR_AVAILABLE = True
    print("✅ PIR motion detector imported successfully")
except ImportError as e:
    print(f"❌ PIR motion detector not available: {e}")
    PIR_DETECTOR_AVAILABLE = False

app = Flask(__name__)

# PIR motion detector instance
pir_detector = None

# PIR motion callback to connect with sighting service
from core.recording.pir_recording_engine import pir_recording_engine

# Imports and Flask setup
from flask import Flask, render_template, request, jsonify, send_file, Response
from flask_cors import CORS
import json
import os
import sys
import sqlite3
import logging
from datetime import datetime, timedelta
import time
import threading

# PIR motion event handler
def handle_pir_motion_event(camera_name: str, motion_event: dict):
    """Handle PIR motion events - trigger recording and save to database"""
    try:
        print(f"🚨 PIR Motion detected: {camera_name}")
        
        # Record motion event in database via sighting service
        if sighting_service:
            motion_data = {
                'camera': camera_name,
                'type': 'gpio',  # PIR sensor type
                'confidence': 0.95,
                'detection_method': motion_event.get('detection_method', 'hardware_motion_sensor'),
                'sensor_type': motion_event.get('sensor_type', 'PIR'),
                'gpio_pin': motion_event.get('gpio_pin'),
                'trigger_type': motion_event.get('trigger_type', 'pir_motion')
            }
            
            # Record the motion event
            timestamp = motion_event.get('timestamp')
            sighting_service._record_motion_event(timestamp, motion_data)
            print(f"✅ Motion event recorded to database: {camera_name}")
        else:
            print(f"❌ Sighting service not available!")
        
        # PIR Recording Logic - start recording on motion detection
        motion_type = motion_event.get('motion_type', 'motion_start')
        if motion_type == 'motion_start':
            print(f"🎬 PIR Motion START - Starting recording for {camera_name}")
            success = pir_recording_engine.start_recording_from_pir(camera_name, motion_event)
            if success:
                print(f"✅ PIR recording started for {camera_name}")
            else:
                print(f"❌ Failed to start PIR recording for {camera_name}")
        elif motion_type == 'motion_continue':
            # Extend existing recording
            pir_recording_engine.extend_recording_from_pir(camera_name, motion_event)
            print(f"⏰ PIR recording extended for {camera_name}")
        else:
            print(f"📊 PIR event recorded: {camera_name} ({motion_type})")
            
    except Exception as e:
        print(f"❌ Error handling PIR motion: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")# Configure CORS for React frontend - Allow all local development ports
CORS(app, origins=[
    "http://localhost:3000",  # React dev server
    "http://localhost:3001",  # React dev server fallback port  
    "http://localhost:3002",  # React dev server port 3002
    "http://localhost:3003",  # React dev server port 3003
    "http://localhost:3004",  # React dev server port 3004
    "http://localhost:3005",  # React dev server port 3005
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001", 
    "http://127.0.0.1:3002",
    "http://127.0.0.1:3003",
    "http://127.0.0.1:3004",
    "http://127.0.0.1:3005",
    "http://10.0.0.82:3000",  # Current Pi IP
    "http://10.0.0.82:3001",  # Current Pi IP fallback ports
    "http://10.0.0.82:3002",  
    "http://10.0.0.82:3003",  
    "http://10.0.0.82:3004",  
    "http://10.0.0.82:3005",  
    "https://*.githubpreview.dev",  # Codespaces preview URLs
    "https://*.app.github.dev"  # Alternative codespace URLs
], supports_credentials=True)

# Import blueprints with error handling
blueprints_config = []

try:
    from dashboard.routes.stream import stream_bp
    blueprints_config.append(('stream', stream_bp, True))
except ImportError as e:
    print(f"Stream module not available: {e}")
    blueprints_config.append(('stream', None, False))

try:
    from dashboard.routes.clips import clips_bp
    blueprints_config.append(('clips', clips_bp, True))
except ImportError as e:
    print(f"Clips module not available: {e}")
    blueprints_config.append(('clips', None, False))

try:
    from dashboard.routes.settings import settings_bp
    blueprints_config.append(('settings', settings_bp, True))
except ImportError as e:
    print(f"Settings module not available: {e}")
    blueprints_config.append(('settings', None, False))

try:
    from dashboard.routes.health import health_bp
    blueprints_config.append(('health', health_bp, True))
except ImportError as e:
    print(f"Health module not available: {e}")
    blueprints_config.append(('health', None, False))

# OLD DASHBOARD MODULE REMOVED - React app at /app is the only dashboard
# try:
#     from routes.dashboard import dashboard_bp
#     blueprints_config.append(('dashboard', dashboard_bp, True))
# except ImportError as e:
#     print(f"Dashboard module not available: {e}")
#     blueprints_config.append(('dashboard', None, False))

try:
    from dashboard.routes.research import research_bp
    blueprints_config.append(('research', research_bp, True))
except ImportError as e:
    print(f"Research module not available: {e}")
    blueprints_config.append(('research', None, False))

# Register available blueprints
for name, blueprint, available in blueprints_config:
    if available and blueprint:
        app.register_blueprint(blueprint)
        print(f"✓ Registered {name} module")
    else:
        print(f"✗ {name} module unavailable")

# API Status endpoint
@app.route('/api/status')
def api_status():
    """API endpoint for React frontend to check backend status"""
    status = {
        'status': 'healthy',
        'version': '1.0.0',
        'modules': {name: available for name, _, available in blueprints_config},
        'api_base': '/api',
        'sighting_service': SIGHTING_SERVICE_AVAILABLE,
        'motion_detection': sighting_service.running if SIGHTING_SERVICE_AVAILABLE else False
    }
    return jsonify(status)

# Real-time Sighting API endpoints
@app.route('/api/sightings')
def api_sightings():
    """Get recent sightings from motion detection, optionally filtered by camera"""
    if not SIGHTING_SERVICE_AVAILABLE:
        return jsonify({'error': 'Sighting service not available'}), 503
        
    try:
        limit = request.args.get('limit', 20, type=int)
        camera = request.args.get('camera', None)  # Optional camera filter
        sightings = sighting_service.get_recent_sightings(limit, camera)
        return jsonify(sightings)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sightings/stats')
def api_sighting_stats():
    """Get sighting statistics"""
    if not SIGHTING_SERVICE_AVAILABLE:
        return jsonify({'error': 'Sighting service not available'}), 503
        
    try:
        stats = sighting_service.get_sighting_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/thumbnails/<path:thumbnail_filename>')
def serve_thumbnail(thumbnail_filename):
    """Serve motion detection thumbnail images"""
    try:
        from flask import send_from_directory
        import os
        
        # Security: only allow access to files in thumbnails directory
        thumbnails_dir = os.path.abspath('./thumbnails')
        if not os.path.exists(thumbnails_dir):
            return jsonify({'error': 'Thumbnails directory not found'}), 404
            
        # Validate filename to prevent directory traversal
        if '..' in thumbnail_filename or '/' in thumbnail_filename or '\\' in thumbnail_filename:
            return jsonify({'error': 'Invalid filename'}), 400
            
        thumbnail_path = os.path.join(thumbnails_dir, thumbnail_filename)
        if not os.path.exists(thumbnail_path):
            return jsonify({'error': 'Thumbnail not found'}), 404
            
        return send_from_directory(thumbnails_dir, thumbnail_filename, mimetype='image/jpeg')
        
    except Exception as e:
        print(f"❌ Error serving thumbnail {thumbnail_filename}: {e}")
        return jsonify({'error': 'Failed to serve thumbnail'}), 500

@app.route('/api/motion/start')
def api_start_motion_detection():
    """Start motion detection system"""
    if not SIGHTING_SERVICE_AVAILABLE:
        return jsonify({'error': 'Sighting service not available'}), 503
        
    try:
        sighting_service.start()
        return jsonify({'status': 'started', 'message': 'Motion detection activated'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/motion/stop')
def api_stop_motion_detection():
    """Stop motion detection system"""
    if not SIGHTING_SERVICE_AVAILABLE:
        return jsonify({'error': 'Sighting service not available'}), 503
        
    try:
        sighting_service.stop_detection()
        return jsonify({'status': 'stopped', 'message': 'Motion detection deactivated'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/motion/status')
def api_motion_status():
    """Get motion detection status"""
    if not SIGHTING_SERVICE_AVAILABLE:
        return jsonify({'error': 'Sighting service not available'}), 503
        
    try:
        # Get basic motion detection status
        status = {
            'running': sighting_service.running,
            'recent_sightings_count': len(sighting_service.recent_sightings)
        }
        
        # Add smart IR LED status
        try:
            from core.infrared.smart_ir_controller import smart_ir_controller
            status['ir_status'] = smart_ir_controller.get_status()
        except ImportError:
            status['ir_status'] = {'ir_available': False, 'message': 'IR controller not available'}
        
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/motion/trigger-test')
def api_trigger_test_sighting():
    """Manually trigger a test sighting for demonstration"""
    try:
        import sqlite3
        from datetime import datetime
        import random
        
        # Connect to database
        conn = sqlite3.connect('/home/p12146/Projects/Nutflix-platform/nutflix.db')
        cur = conn.cursor()
        
        # Create a realistic sighting
        timestamp = datetime.now().isoformat()
        species = "Human"  # Since user is testing
        behavior = "investigating"
        confidence = 0.92
        camera = random.choice(['CritterCam', 'NestCam'])
        
        cur.execute('''
            INSERT INTO clip_metadata (timestamp, species, behavior, confidence, camera, motion_zone)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (timestamp, species, behavior, confidence, camera, 'center'))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'message': f'Test sighting added: {species} detected on {camera}',
            'sighting': {
                'species': species,
                'behavior': behavior,
                'confidence': confidence,
                'camera': camera,
                'timestamp': timestamp
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/latest_clip/<camera_id>')
def get_latest_clip(camera_id):
    """Get latest PIR-triggered clip data for a camera"""
    try:
        # Normalize camera ID
        original_camera_id = camera_id
        camera_id = camera_id.lower()
        
        # Map frontend camera names to backend names
        camera_map = {
            'nestcam': 'NestCam',
            'crittercam': 'CritterCam',
            'camera-1': 'NestCam',
            'camera-2': 'CritterCam', 
            'camera-3': 'NestCam',
            'camera-4': 'CritterCam',
            'camera-5': 'NestCam',
            'camera-6': 'CritterCam'
        }
        backend_camera_name = camera_map.get(camera_id, camera_id.title())
        
        # Get latest clip from database
        conn = sqlite3.connect('/home/p12146/Projects/Nutflix-platform/nutflix.db')
        cur = conn.cursor()
        
        cur.execute('''
            SELECT timestamp, camera, clip_path, thumbnail_path, duration, 
                   trigger_type, has_audio, species, behavior, confidence, created_at
            FROM clip_metadata 
            WHERE camera = ?
            ORDER BY created_at DESC 
            LIMIT 1
        ''', (backend_camera_name,))
        
        result = cur.fetchone()
        conn.close()
        
        if result:
            (timestamp, camera, clip_path, thumbnail_path, duration, 
             trigger_type, has_audio, species, behavior, confidence, created_at) = result
            
            # Calculate time since clip
            try:
                clip_time = datetime.fromisoformat(timestamp)
                minutes_ago = int((datetime.now() - clip_time).total_seconds() / 60)
            except:
                minutes_ago = None
            
            return jsonify({
                'has_clip': True,
                'last_seen_minutes': minutes_ago,
                'thumbnail_url': thumbnail_path,
                'timestamp': timestamp,
                'trigger_type': trigger_type or 'pir_motion',
                'camera': camera,
                'duration': duration or 0,
                'has_audio': bool(has_audio),
                'species': species or 'Wildlife',
                'behavior': behavior or 'investigating',
                'confidence': confidence or 0.95,
                'clip_path': clip_path
            })
        else:
            # No clips found for this camera
            return jsonify({
                'has_clip': False,
                'last_seen_minutes': None,
                'thumbnail_url': None,
                'message': f'No recordings yet for {backend_camera_name}',
                'camera': backend_camera_name
            })
        
    except Exception as e:
        print(f"[latest_clip] Error for {camera_id}: {e}")
        return jsonify({
            'has_clip': False,
            'last_seen_minutes': None,
            'thumbnail_url': None,
            'error': str(e),
            'camera': backend_camera_name
        }), 500

@app.route('/api/clip_thumbnail/<camera_id>')
def get_clip_thumbnail(camera_id):
    """Get thumbnail from latest clip for a camera"""
    try:
        print(f"🔍 Thumbnail request for camera_id: {camera_id}")
        
        # NEW: Try to get actual clip thumbnail from database
        try:
            import sqlite3
            from pathlib import Path  # NEW: Import Path for file operations
            
            # Map frontend camera names to backend names
            camera_map = {
                'nestcam': 'NestCam',
                'crittercam': 'CritterCam',
                'camera-1': 'NestCam',
                'camera-2': 'CritterCam', 
                'camera-3': 'NestCam',
                'camera-4': 'CritterCam',
                'camera-5': 'NestCam',
                'camera-6': 'CritterCam'
            }
            backend_camera_name = camera_map.get(camera_id.lower(), camera_id)
            
            # Query for latest clip with thumbnail for this camera
            conn = sqlite3.connect('/home/p12146/Projects/Nutflix-platform/nutflix.db')
            cur = conn.cursor()
            
            cur.execute('''
                SELECT clip_path FROM clip_metadata 
                WHERE camera = ? AND clip_path IS NOT NULL
                ORDER BY created_at DESC 
                LIMIT 1
            ''', (backend_camera_name,))
            
            result = cur.fetchone()
            conn.close()
            
            if result:
                clip_path = result[0]
                # Look for thumbnail next to the clip
                clip_path_obj = Path(clip_path)
                thumbnail_path = clip_path_obj.with_suffix('.jpg')
                
                if thumbnail_path.exists():
                    print(f"📸 Serving clip thumbnail: {thumbnail_path}")
                    return send_from_directory(
                        thumbnail_path.parent,
                        thumbnail_path.name,
                        mimetype='image/jpeg'
                    )
                else:
                    print(f"⚠️ Thumbnail not found: {thumbnail_path}")
            else:
                print(f"⚠️ No clips found for camera: {backend_camera_name}")
                
        except Exception as db_error:
            print(f"❌ Database query error: {db_error}")
        
        # Fallback to live camera thumbnail
        live_thumbnail_url = f'/api/stream/{camera_id}/thumbnail'
        print(f"🔄 Redirecting to live thumbnail: {live_thumbnail_url}")
        return redirect(live_thumbnail_url)
            
    except Exception as e:
        print(f"❌ Error getting clip thumbnail for {camera_id}: {e}")
        # Fallback to live thumbnail
        return redirect(f'/api/stream/{camera_id}/thumbnail')

@app.route('/api/clip/thumbnail')
def get_clip_thumbnail_by_path():
    """Generate and serve thumbnail from clip path"""
    try:
        clip_path = request.args.get('path')
        if not clip_path:
            return jsonify({'error': 'Missing clip path parameter'}), 400
            
        print(f"🔍 Generating thumbnail for clip: {clip_path}")
        
        # Convert relative path to absolute path
        if not clip_path.startswith('/home/p12146/Projects/Nutflix-platform'):
            clip_path = os.path.join('/home/p12146/Projects/Nutflix-platform', clip_path.lstrip('/'))
        
        clip_file = Path(clip_path)
        
        # Check if clip file exists
        if not clip_file.exists():
            print(f"❌ Clip file not found: {clip_path}")
            return jsonify({'error': 'Clip file not found'}), 404
        
        # Generate thumbnail path
        thumbnail_path = clip_file.with_suffix('.jpg')
        
        # Generate thumbnail if it doesn't exist
        if not thumbnail_path.exists():
            try:
                import subprocess
                print(f"🎬 Generating thumbnail from clip: {clip_path}")
                
                # Use ffmpeg to extract thumbnail from the middle of the video
                cmd = [
                    'ffmpeg', '-i', str(clip_file),
                    '-ss', '00:00:05',  # Take frame at 5 seconds
                    '-vframes', '1',
                    '-y',  # Overwrite output file
                    str(thumbnail_path)
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    print(f"❌ FFmpeg error: {result.stderr}")
                    return jsonify({'error': 'Failed to generate thumbnail'}), 500
                    
                print(f"✅ Thumbnail generated: {thumbnail_path}")
                
            except Exception as gen_error:
                print(f"❌ Error generating thumbnail: {gen_error}")
                return jsonify({'error': 'Failed to generate thumbnail'}), 500
        
        # Serve the thumbnail
        if thumbnail_path.exists():
            return send_from_directory(
                thumbnail_path.parent,
                thumbnail_path.name,
                mimetype='image/jpeg'
            )
        else:
            return jsonify({'error': 'Thumbnail not available'}), 404
            
    except Exception as e:
        print(f"❌ Error generating clip thumbnail: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/clips/<path:clip_path>')
def serve_video_clip(clip_path):
    """
    Serve video clip files with automatic H.264 version preference
    
    Priority order:
    1. Check for pre-converted H.264 version (*_h264.mp4)
    2. Fall back to original file if no H.264 version exists
    
    This ensures optimal browser compatibility without on-the-fly conversion.
    """
    try:
        # Construct the full path to the video file
        project_root = Path(__file__).parent.parent
        original_clip_path = project_root / clip_path
        
        # Check for H.264 converted version first
        if original_clip_path.suffix.lower() == '.mp4':
            # Create H.264 version path: /path/filename.mp4 -> /path/filename_h264.mp4
            h264_clip_path = original_clip_path.with_name(f"{original_clip_path.stem}_h264.mp4")
            
            if h264_clip_path.exists():
                print(f"🎬 Serving H.264 version: {h264_clip_path.name}")
                actual_file_path = h264_clip_path
            elif original_clip_path.exists():
                print(f"🎬 Serving original file (H.264 version not available): {original_clip_path.name}")
                actual_file_path = original_clip_path
            else:
                print(f"❌ Video file not found: {original_clip_path}")
                return jsonify({'error': 'Video file not found'}), 404
        else:
            # Non-MP4 files, serve as-is
            if original_clip_path.exists():
                print(f"🎬 Serving non-MP4 file: {original_clip_path.name}")
                actual_file_path = original_clip_path
            else:
                print(f"❌ Video file not found: {original_clip_path}")
                return jsonify({'error': 'Video file not found'}), 404
        
        # Validate file is a video format
        if actual_file_path.suffix.lower() in ['.mp4', '.avi', '.mov']:
            # Create response with enhanced headers for browser compatibility
            response = make_response(send_file(
                actual_file_path,
                mimetype='video/mp4',
                as_attachment=False
            ))
            
            # Essential headers for video streaming
            response.headers['Accept-Ranges'] = 'bytes'
            response.headers['Content-Type'] = 'video/mp4'
            response.headers['Cache-Control'] = 'public, max-age=3600'  # 1 hour cache for static videos
            
            # CORS headers for cross-origin requests
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, HEAD, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Range, Content-Type, Accept-Encoding'
            response.headers['Access-Control-Expose-Headers'] = 'Content-Length, Accept-Ranges'
            
            print(f"✅ Successfully serving: {actual_file_path.name}")
            return response
        else:
            print(f"❌ Unsupported video format: {actual_file_path}")
            return jsonify({'error': 'Unsupported video format'}), 415
            
    except Exception as e:
        print(f"❌ Error serving video clip: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/clips-compat/<path:clip_path>')
def serve_video_clip_compatible(clip_path):
    """Serve video clip files with on-the-fly conversion for browser compatibility"""
    try:
        # Construct the full path to the video file
        project_root = Path(__file__).parent.parent
        full_clip_path = project_root / clip_path
        
        print(f"🎬 Serving compatible video clip: {full_clip_path}")
        
        if full_clip_path.exists() and full_clip_path.suffix.lower() in ['.mp4', '.avi', '.mov']:
            # Try to convert using ffmpeg for better browser compatibility
            import subprocess
            import tempfile
            import threading
            
            def stream_converted_video():
                try:
                    # Use ffmpeg to convert to H.264 on-the-fly
                    process = subprocess.Popen([
                        'ffmpeg', '-i', str(full_clip_path),
                        '-c:v', 'libx264',  # H.264 codec
                        '-preset', 'ultrafast',  # Fast encoding
                        '-crf', '28',  # Reasonable quality/size balance
                        '-f', 'mp4',  # MP4 container
                        '-movflags', 'frag_keyframe+empty_moov',  # Web optimization
                        'pipe:1'  # Output to stdout
                    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    
                    while True:
                        chunk = process.stdout.read(8192)
                        if not chunk:
                            break
                        yield chunk
                        
                    process.wait()
                except Exception as e:
                    print(f"❌ Error converting video: {e}")
                    yield b''
            
            response = Response(
                stream_converted_video(),
                mimetype='video/mp4',
                headers={
                    'Accept-Ranges': 'bytes',
                    'Content-Type': 'video/mp4',
                    'Cache-Control': 'no-cache',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, OPTIONS',
                    'Access-Control-Allow-Headers': 'Range, Content-Type'
                }
            )
            return response
            
        else:
            print(f"❌ Video file not found: {full_clip_path}")
            return jsonify({'error': 'Video file not found'}), 404
            
    except Exception as e:
        print(f"❌ Error serving compatible video clip: {e}")
        # Fallback to original method
        return serve_video_clip(clip_path)

# Serve React static files in production
@app.route('/static/<path:path>')
@app.route('/app/static/<path:path>')
def serve_static(path):
    """Serve React static files (CSS, JS, etc.)"""
    frontend_build = Path(__file__).parent.parent / 'frontend' / 'build'
    static_path = frontend_build / 'static' / path
    
    if static_path.exists():
        return send_from_directory(frontend_build / 'static', path)
    else:
        return "Static file not found", 404

@app.route('/health')
def fallback_health():
    return jsonify({
        'status': 'healthy',
        'modules': {name: available for name, _, available in blueprints_config}
    })

@app.route('/')
def home():
    """Root route - redirect to main React dashboard"""
    return redirect('/app')

@app.route('/app')
@app.route('/app/<path:path>')
def serve_react_app(path=''):
    """MAIN DASHBOARD - Serve React app (the only dashboard we use)"""
    frontend_build = Path(__file__).parent.parent / 'frontend' / 'build'
    
    if not frontend_build.exists():
        return jsonify({
            'error': 'React frontend not built',
            'message': 'Run "npm run build" in the frontend directory'
        }), 404
    
    # Handle static files
    if path.startswith('static/'):
        static_file = path[7:]  # Remove 'static/' prefix
        return serve_static(static_file)
    # Handle other assets (favicon, manifest, etc.)
    elif path and (frontend_build / path).exists():
        return send_from_directory(frontend_build, path)
    else:
        # Always serve React index.html for the main app
        return send_from_directory(frontend_build, 'index.html')

if __name__ == '__main__':    
    # Start sighting service if available
    if SIGHTING_SERVICE_AVAILABLE:
        print("🚀 Starting motion detection and sighting service...")
        try:
            # Connect camera manager for streaming (PIR sensors handle motion detection)
            from core.camera.camera_manager import CameraManager
            camera_manager = CameraManager("nutpod")
            print("📹 Camera manager initialized")
            
            # Share camera manager with stream routes first
            try:
                from routes import stream
                # Pass the camera manager to the stream module
                stream.cam_mgr = camera_manager
                stream.CAMERA_AVAILABLE = True
                # Also add to app context for routes that need it
                app.camera_manager = camera_manager
                print("📹 Camera manager shared with stream routes")
            except Exception as e:
                print(f"❌ Could not share camera manager with stream routes: {e}")
            
            # Connect camera manager to sighting service for motion detection
            sighting_service.connect_camera_manager(camera_manager)
            print("🔗 Camera manager connected to sighting service")
            
            # Update PIR recording engine with camera manager
            pir_recording_engine.camera_manager = camera_manager
            print("🎬 PIR Recording Engine ready for motion-triggered recording")
            
            # Start the motion detection system
            sighting_service.start()
            print("✅ Motion detection started")
        except Exception as e:
            print(f"❌ Failed to start sighting service: {e}")
    
    # Initialize PIR motion detection
    if PIR_DETECTOR_AVAILABLE and SIGHTING_SERVICE_AVAILABLE:
        print("🚨 Initializing PIR motion detection...")
        
        # Define PIR callback to use our motion handler
        def pir_motion_callback(camera_name: str, motion_event: dict):
            handle_pir_motion_event(camera_name, motion_event)
        
        try:
            pir_detector = DualPIRMotionDetector(motion_callback=pir_motion_callback)
            pir_detector.start_detection()
            print("✅ PIR motion detector started for both cameras")
        except Exception as e:
            print(f"❌ Failed to start PIR motion detector: {e}")
    else:
        print(f"❌ PIR motion detection NOT started:")
        print(f"   PIR_DETECTOR_AVAILABLE={PIR_DETECTOR_AVAILABLE}")
        print(f"   SIGHTING_SERVICE_AVAILABLE={SIGHTING_SERVICE_AVAILABLE}")
    
    # PIR Recording Engine is automatically available as global instance
    print("🎬 PIR Recording Engine ready for motion-triggered recording")
    
    app.run(host='0.0.0.0', port=8001, debug=False)
