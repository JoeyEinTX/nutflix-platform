
import os
import datetime
from flask import Blueprint, render_template, current_app, url_for
from core.storage.file_manager import FileManager
from utils.env_sensor import EnvSensor

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route("/dashboard")
def dashboard():
    config = current_app.config.get("DEVICE_CONFIG", {})
    device_name = config.get("device_name", "SquirrelBox")
    # Support both old and new config formats
    cameras = config.get("cameras")
    if not cameras:
        # fallback for flat config: enabled_cameras list
        cameras = [{"name": cam, "role": "Unknown"} for cam in config.get("enabled_cameras", [])]

    fm = FileManager(device_name)
    # Read environmental sensor data
    env_sensor = EnvSensor()
    env_data = env_sensor.read()

    camera_data = []
    for cam in cameras:
        name = cam.get("name") if isinstance(cam, dict) else cam
        role = cam.get("role", "Unknown") if isinstance(cam, dict) else "Unknown"
        snapshot_path = fm.get_latest_snapshot(name)

        if snapshot_path:
            snapshot_url = url_for('static', filename=f"recordings/{snapshot_path.name}")
            last_seen = datetime.datetime.fromtimestamp(snapshot_path.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        else:
            snapshot_url = url_for('static', filename='images/placeholder.jpg')
            last_seen = "No recent activity"

        camera_data.append({
            "name": name,
            "role": role,
            "snapshot_url": snapshot_url,
            "last_seen": last_seen,
        })

    sightings = fm.list_recent_clips(limit=10)

    return render_template(
        "dashboard.html",
        device_name=device_name,
        camera_data=camera_data,
        sightings=sightings,
        env_data=env_data
    )
