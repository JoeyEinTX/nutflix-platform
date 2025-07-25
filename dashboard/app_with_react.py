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

from flask import Flask, redirect, url_for, render_template, jsonify, send_from_directory, request
from flask_cors import CORS

# Import sighting service
try:
    from core.sighting_service import sighting_service
    SIGHTING_SERVICE_AVAILABLE = True
    print("✅ Sighting service imported successfully")
except ImportError as e:
    print(f"❌ Sighting service not available: {e}")
    SIGHTING_SERVICE_AVAILABLE = False

app = Flask(__name__)

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

try:
    from routes.dashboard import dashboard_bp
    blueprints_config.append(('dashboard', dashboard_bp, True))
except ImportError as e:
    print(f"Dashboard module not available: {e}")
    blueprints_config.append(('dashboard', None, False))

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

@app.route('/api/motion/start')
def api_start_motion_detection():
    """Start motion detection system"""
    if not SIGHTING_SERVICE_AVAILABLE:
        return jsonify({'error': 'Sighting service not available'}), 503
        
    try:
        sighting_service.start_detection()
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
        return jsonify({
            'running': sighting_service.running,
            'recent_sightings_count': len(sighting_service.recent_sightings)
        })
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

# Serve React static files in production
@app.route('/app/static/<path:path>')
def serve_static(path):
    """Serve React static files (CSS, JS, etc.)"""
    frontend_build = Path(__file__).parent.parent / 'frontend' / 'build'
    static_path = frontend_build / 'static' / path
    
    if static_path.exists():
        return send_from_directory(frontend_build / 'static', path)
    else:
        return "Static file not found", 404

@app.route('/app')
@app.route('/app/<path:path>')
def serve_react_app(path=''):
    """Serve React app static files"""
    frontend_build = Path(__file__).parent.parent / 'frontend' / 'build'
    
    if frontend_build.exists():
        # Handle static files
        if path.startswith('static/'):
            static_file = path[7:]  # Remove 'static/' prefix
            return serve_static(static_file)
        # Handle other assets (favicon, manifest, etc.)
        elif path and (frontend_build / path).exists():
            return send_from_directory(frontend_build, path)
        else:
            return send_from_directory(frontend_build, 'index.html')
    else:
        return jsonify({
            'error': 'React frontend not built',
            'message': 'Run "npm run build" in the frontend directory'
        }), 404

# Fallback endpoints for missing modules
@app.route('/clips')
def fallback_clips():
    return render_template('clips.html') if Path('templates/clips.html').exists() else jsonify({'error': 'Clips module not available'})

@app.route('/settings') 
def fallback_settings():
    return render_template('settings.html') if Path('templates/settings.html').exists() else jsonify({'error': 'Settings module not available'})

@app.route('/health')
def fallback_health():
    return jsonify({
        'status': 'healthy',
        'modules': {name: available for name, _, available in blueprints_config}
    })

@app.route('/')
def home():
    """Home route - redirect to React app or fallback to dashboard"""
    frontend_build = Path(__file__).parent.parent / 'frontend' / 'build'
    
    if frontend_build.exists():
        return redirect('/app')
    else:
        # Fallback to existing dashboard
        for name, _, available in blueprints_config:
            if name == 'dashboard' and available:
                return redirect('/dashboard')
            elif name == 'clips' and available:
                return redirect('/clips')
        
        return jsonify({
            'message': 'Nutflix Platform API',
            'frontend': 'React app not built - run "npm run build" in frontend/',
            'api_docs': '/api/status'
        })

if __name__ == '__main__':
    # Start sighting service if available
    if SIGHTING_SERVICE_AVAILABLE:
        print("🚀 Starting motion detection and sighting service...")
        try:
            sighting_service.start_detection()
        except Exception as e:
            print(f"❌ Failed to start sighting service: {e}")
    
    app.run(host='0.0.0.0', port=8000, debug=False)
