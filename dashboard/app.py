import sys
import os
# Add the parent directory to Python path so we can import 'core'
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, redirect, url_for, render_template

# Try to import the blueprints, with fallbacks for missing dependencies
try:
    from routes.stream import stream_bp
    STREAM_AVAILABLE = True
except ImportError as e:
    print(f"Stream module not available: {e}")
    stream_bp = None
    STREAM_AVAILABLE = False

try:
    from routes.clips import clips_bp
    CLIPS_AVAILABLE = True
except ImportError as e:
    print(f"Clips module not available: {e}")
    clips_bp = None
    CLIPS_AVAILABLE = False

try:
    from routes.settings import settings_bp
    SETTINGS_AVAILABLE = True
except ImportError as e:
    print(f"Settings module not available: {e}")
    settings_bp = None
    SETTINGS_AVAILABLE = False

try:
    from routes.health import health_bp
    HEALTH_AVAILABLE = True
except ImportError as e:
    print(f"Health module not available: {e}")
    health_bp = None
    HEALTH_AVAILABLE = False

try:
    from routes.dashboard import dashboard_bp
    DASHBOARD_AVAILABLE = True
except ImportError as e:
    print(f"Dashboard module not available: {e}")
    dashboard_bp = None
    DASHBOARD_AVAILABLE = False

app = Flask(__name__, static_folder='static', template_folder='templates')

# Register blueprints only if they're available
if STREAM_AVAILABLE and stream_bp:
    app.register_blueprint(stream_bp, url_prefix='/stream')
    print("✓ Stream module registered")

if CLIPS_AVAILABLE and clips_bp:
    app.register_blueprint(clips_bp, url_prefix='/clips')
    print("✓ Clips module registered")

if SETTINGS_AVAILABLE and settings_bp:
    app.register_blueprint(settings_bp, url_prefix='/settings')
    print("✓ Settings module registered")

if HEALTH_AVAILABLE and health_bp:
    app.register_blueprint(health_bp, url_prefix='/health')
    print("✓ Health module registered")

if DASHBOARD_AVAILABLE and dashboard_bp:
    app.register_blueprint(dashboard_bp, url_prefix='')
    print("✓ Dashboard module registered")

# Fallback routes if modules aren't available
if not DASHBOARD_AVAILABLE:
    @app.route('/dashboard')
    def fallback_dashboard():
        return render_template('dashboard.html')

if not CLIPS_AVAILABLE:
    @app.route('/clips')
    def fallback_clips():
        return render_template('clips.html', files=[])

if not SETTINGS_AVAILABLE:
    @app.route('/settings')
    def fallback_settings():
        return render_template('settings.html')

if not HEALTH_AVAILABLE:
    @app.route('/health')
    def fallback_health():
        return {'status': 'healthy', 'modules': {
            'stream': STREAM_AVAILABLE,
            'clips': CLIPS_AVAILABLE, 
            'settings': SETTINGS_AVAILABLE,
            'dashboard': DASHBOARD_AVAILABLE
        }}

@app.route('/')
def home():
    # Try dashboard first, then clips, then render a basic page
    if DASHBOARD_AVAILABLE:
        return redirect('/dashboard')
    elif CLIPS_AVAILABLE:
        return redirect('/clips')
    else:
        return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
