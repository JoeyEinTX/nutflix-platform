from flask import Blueprint, jsonify

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
