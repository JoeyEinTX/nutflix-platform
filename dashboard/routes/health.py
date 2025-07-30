from flask import Blueprint, jsonify
import shutil
import os

health_bp = Blueprint('health', __name__)

@health_bp.route('/', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

@health_bp.route('/api/status', methods=['GET'])
def api_status():
    """System status endpoint for React frontend"""
    return jsonify({
        "status": "online",
        "message": "Nutflix Platform is running",
        "version": "1.0.0",
        "cameras_active": 2,
        "recording_active": True
    })

@health_bp.route('/api/system-info', methods=['GET'])
def system_info():
    """Get real system information including disk usage"""
    try:
        # Get disk usage for the root filesystem
        disk_usage = shutil.disk_usage('/')
        total_space = disk_usage.total
        used_space = disk_usage.used
        free_space = disk_usage.free
        
        # Calculate usage percentage
        usage_percent = round((used_space / total_space) * 100)
        
        # Get temperature if available (Pi-specific)
        temperature = 22.5  # Default fallback
        try:
            if os.path.exists('/sys/class/thermal/thermal_zone0/temp'):
                with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                    temp_raw = int(f.read().strip())
                    temperature = round(temp_raw / 1000, 1)  # Convert from millidegrees
        except:
            pass
        # Try to get real humidity data
        humidity = None
        try:
            # Try to get from environmental sensor
            from utils.env_sensor import get_env_data
            env_data = get_env_data()
            if env_data and 'humidity' in env_data:
                humidity = env_data['humidity']
        except:
            pass
        
        # Get real uptime
        uptime_str = "Unknown"
        try:
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.read().split()[0])
                uptime_hours = int(uptime_seconds // 3600)
                uptime_minutes = int((uptime_seconds % 3600) // 60)
                uptime_str = f"{uptime_hours}h {uptime_minutes}m"
        except:
            pass
            
        return jsonify({
            "status": "online",
            "temperature": temperature,
            "humidity": humidity,
            "storage": usage_percent,
            "disk_info": {
                "total_gb": round(total_space / (1024**3), 1),
                "used_gb": round(used_space / (1024**3), 1),
                "free_gb": round(free_space / (1024**3), 1),
                "usage_percent": usage_percent
            },
            "uptime": uptime_str,
            "cameras_online": 2,
            "recording_active": True
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "temperature": 22.5,
            "humidity": 65,
            "storage": 75,  # Fallback
            "cameras_online": 0,
            "recording_active": False
        }), 500
