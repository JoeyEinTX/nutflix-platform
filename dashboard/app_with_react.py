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

from flask import Flask, redirect, url_for, render_template, jsonify, send_from_directory, request, Response
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

# NEW: Import RecordingEngine for clip recording
try:
    from core.recording_engine import RecordingEngine
    RECORDING_ENGINE_AVAILABLE = True
    print("✅ RecordingEngine imported successfully")
except ImportError as e:
    print(f"❌ RecordingEngine not available: {e}")
    RECORDING_ENGINE_AVAILABLE = False

app = Flask(__name__)

# PIR motion detector instance
pir_detector = None

# NEW: RecordingEngine instance for clip recording
recording_engine = None

# PIR motion callback to connect with sighting service
def pir_motion_callback(camera_name: str, motion_event: dict):
    """Handle PIR motion detection events"""
    global recording_engine  # NEW: Access global recording_engine instance
    
    try:
        print(f"🚨 PIR Motion detected: {camera_name}")
        
        if SIGHTING_SERVICE_AVAILABLE:
            # Create motion data compatible with sighting service
            motion_data = {
                'camera': camera_name,
                'motion_type': 'gpio',  # PIR sensor type
                'confidence': 0.95,     # PIR sensors are very reliable
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
        
        # NEW: Smart clip recording logic - only on motion START
        motion_type = motion_event.get('motion_type', 'unknown')
        if RECORDING_ENGINE_AVAILABLE and recording_engine and motion_type == 'MOTION_START':
            try:
                print(f"🎬 PIR Motion START - Starting/extending clip recording for {camera_name}")
                success = recording_engine.start_recording(
                    camera_id=camera_name,
                    duration=10.0,  # 10 seconds after motion ends
                    trigger_type='pir_motion'
                )
                if success:
                    print(f"✅ Recording started/extended for {camera_name}")
                else:
                    print(f"❌ Failed to start recording for {camera_name}")
            except Exception as recording_error:
                print(f"❌ Recording error for {camera_name}: {recording_error}")
        elif RECORDING_ENGINE_AVAILABLE and motion_type == 'MOTION_END':
            print(f"🏁 PIR Motion END - {camera_name} recording will continue for 10s timeout")
        else:
            if not RECORDING_ENGINE_AVAILABLE:
                print(f"❌ RecordingEngine not available for {camera_name}")
            else:
                print(f"📊 PIR event recorded: {camera_name} ({motion_type})")
            
    except Exception as e:
        print(f"❌ Error handling PIR motion: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")

# Configure CORS for React frontend
CORS(app, origins=[
    "http://localhost:3000",  # React dev server
    "http://127.0.0.1:3000",
    "http://10.0.0.79:3000",  # Network access
    "https://*.githubpreview.dev",  # Codespaces preview URLs
    "https://*.app.github.dev"  # Alternative codespace URLs
])

# Import blueprints with error handling
blueprints_config = []

try:
    from routes.stream import stream_bp
    blueprints_config.append(('stream', stream_bp, True))
except ImportError as e:
    print(f"Stream module not available: {e}")
    blueprints_config.append(('stream', None, False))

try:
    from routes.clips import clips_bp
    blueprints_config.append(('clips', clips_bp, True))
except ImportError as e:
    print(f"Clips module not available: {e}")
    blueprints_config.append(('clips', None, False))

try:
    from routes.settings import settings_bp
    blueprints_config.append(('settings', settings_bp, True))
except ImportError as e:
    print(f"Settings module not available: {e}")
    blueprints_config.append(('settings', None, False))

try:
    from routes.health import health_bp
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
    from routes.research import research_bp
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
        conn = sqlite3.connect('/home/p12146/NutFlix/nutflix-platform/nutflix.db')
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
    """Get latest clip/motion event data for a camera"""
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
        
        if not CLIP_MANAGER_AVAILABLE:
            # Fallback to sighting service if available
            if SIGHTING_SERVICE_AVAILABLE:
                recent_sightings = sighting_service.get_recent_sightings(limit=1, camera=backend_camera_name)
                if recent_sightings:
                    sighting = recent_sightings[0]
                    # Calculate time since last sighting
                    try:
                        # Try to parse the raw_timestamp if available, otherwise timestamp
                        timestamp_str = sighting.get('raw_timestamp', sighting.get('timestamp', ''))
                        if timestamp_str:
                            # Handle different timestamp formats
                            if 'T' in timestamp_str:
                                sighting_time = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                            else:
                                sighting_time = datetime.strptime(timestamp_str, '%B %d, %Y %I:%M %p')
                            minutes_ago = int((datetime.now() - sighting_time).total_seconds() / 60)
                        else:
                            minutes_ago = 0
                    except Exception as e:
                        print(f"Error parsing timestamp {timestamp_str}: {e}")
                        minutes_ago = 0
                    
                    return jsonify({
                        'camera_id': camera_id,
                        'has_clip': True,
                        'last_seen_minutes': minutes_ago,
                        'thumbnail_url': f'/api/stream/{camera_id}/thumbnail',  # Fallback to live thumbnail
                        'timestamp': sighting['timestamp'],
                        'trigger_type': 'motion',
                        'species': sighting.get('species', 'Unknown'),
                        'confidence': sighting.get('confidence', 0.0)
                    })
            
            # No clip data available
            return jsonify({
                'camera_id': camera_id,
                'has_clip': False,
                'last_seen_minutes': None,
                'thumbnail_url': None,
                'timestamp': None,
                'trigger_type': None,
                'message': 'No sightings yet'
            })
        
        # Use ClipManager to get latest clip
        clip_manager = ClipManager()
        
        backend_camera_id = backend_camera_name
        
        # Get recent clips for this camera
        clips = clip_manager.scan_clips(camera_id=backend_camera_id, days_back=7)
        
        if not clips:
            return jsonify({
                'camera_id': camera_id,
                'has_clip': False,
                'last_seen_minutes': None,
                'thumbnail_url': None,
                'timestamp': None,
                'trigger_type': None,
                'message': 'No clips yet'
            })
        
        # Get the most recent clip
        latest_clip = clips[0]  # clips are sorted by timestamp (newest first)
        
        # Calculate minutes since the clip
        minutes_ago = int((datetime.now() - latest_clip.timestamp).total_seconds() / 60)
        
        # Try to create a thumbnail from the clip (for now, fallback to placeholder)
        thumbnail_url = f'/api/clip_thumbnail/{camera_id}'
        
        response_data = {
            'camera_id': camera_id,
            'has_clip': True,
            'last_seen_minutes': minutes_ago,
            'thumbnail_url': thumbnail_url,
            'timestamp': latest_clip.timestamp.isoformat(),
            'trigger_type': latest_clip.trigger_type,
            'filename': latest_clip.filename,
            'file_size': latest_clip.file_size,
            'duration': latest_clip.duration
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"❌ Error getting latest clip for {camera_id}: {e}")
        return jsonify({
            'camera_id': camera_id,
            'has_clip': False,
            'error': str(e),
            'message': 'Error retrieving clip data'
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
            conn = sqlite3.connect('/home/p12146/NutFlix/nutflix-platform/nutflix.db')
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
            # Initialize and connect camera manager for vision-based motion detection
            from core.camera.camera_manager import CameraManager
            camera_manager = CameraManager("nutpod")
            print("📹 Camera manager initialized")
            
            # Share camera manager with stream routes first
            try:
                from routes import stream
                # Pass the camera manager to the stream module
                stream.cam_mgr = camera_manager
                stream.CAMERA_AVAILABLE = True
                print("📹 Camera manager shared with stream routes")
            except Exception as e:
                print(f"❌ Could not share camera manager with stream routes: {e}")
            
            # Connect camera manager to sighting service for motion detection
            sighting_service.connect_camera_manager(camera_manager)
            print("🔗 Camera manager connected to sighting service")
            
            # Start the motion detection system
            sighting_service.start()
            print("✅ Motion detection started")
        except Exception as e:
            print(f"❌ Failed to start sighting service: {e}")
    
    # Initialize PIR motion detection
    if PIR_DETECTOR_AVAILABLE and SIGHTING_SERVICE_AVAILABLE:
        print("🚨 Initializing PIR motion detection...")
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
    
    # NEW: Initialize RecordingEngine for clip recording
    if RECORDING_ENGINE_AVAILABLE:
        print("🎬 Initializing RecordingEngine...")
        try:
            # Pass the shared camera_manager to avoid conflicts
            recording_engine = RecordingEngine(camera_manager=camera_manager)
            print("✅ RecordingEngine initialized successfully with shared camera manager")
        except Exception as e:
            print(f"❌ Failed to initialize RecordingEngine: {e}")
            recording_engine = None
    else:
        print("❌ RecordingEngine not available")
        recording_engine = None
    
    app.run(host='0.0.0.0', port=8000, debug=False)
