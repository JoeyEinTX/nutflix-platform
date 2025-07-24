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

from flask import Flask, redirect, url_for, render_template, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__)

# Configure CORS for React frontend
CORS(app, origins=[
    "http://localhost:3000",  # React dev server
    "http://127.0.0.1:3000",
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
        'api_base': '/api'
    }
    return jsonify(status)

# Serve React static files in production
@app.route('/app')
@app.route('/app/<path:path>')
def serve_react_app(path=''):
    """Serve React app static files"""
    frontend_build = Path(__file__).parent.parent / 'frontend' / 'build'
    
    if frontend_build.exists():
        if path and (frontend_build / path).exists():
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
    app.run(host='0.0.0.0', port=8000, debug=True)
