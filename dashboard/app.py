import sys
import os
# Add the parent directory to Python path so we can import 'core'
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, redirect, url_for
from routes.stream import stream_bp
from routes.clips import clips_bp
from routes.settings import settings_bp
from routes.health import health_bp
from routes.dashboard import dashboard_bp

app = Flask(__name__, static_folder='static', template_folder='templates')

# Register blueprints
app.register_blueprint(stream_bp, url_prefix='/stream')
app.register_blueprint(clips_bp, url_prefix='/clips')
app.register_blueprint(settings_bp, url_prefix='/settings')
app.register_blueprint(health_bp, url_prefix='/health')
app.register_blueprint(dashboard_bp, url_prefix='')

@app.route('/')
def home():
    return redirect(url_for('clips.index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
