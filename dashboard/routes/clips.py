from flask import Blueprint, render_template, current_app
import os

clips_bp = Blueprint('clips', __name__)

@clips_bp.route('/')
def index():
    recordings_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'recordings')
    try:
        files = [f for f in os.listdir(recordings_dir) if os.path.isfile(os.path.join(recordings_dir, f))]
        files.sort(reverse=True)
    except Exception as e:
        files = []
        print(f"[clips_bp] Error listing recordings: {e}")
    return render_template('clips.html', files=files)
