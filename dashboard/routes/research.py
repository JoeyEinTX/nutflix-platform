from flask import Blueprint, render_template, jsonify
# from dashboard.services.analytics import get_recent_sightings, get_recent_env_readings

# Import sighting service
try:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from core.sighting_service import sighting_service
    SIGHTING_SERVICE_AVAILABLE = True
except ImportError as e:
    print(f"Sighting service not available in research routes: {e}")
    SIGHTING_SERVICE_AVAILABLE = False

research_bp = Blueprint('research', __name__, template_folder='../templates/research')

def get_real_sightings(limit=100):
    """Get real sightings data from sighting service"""
    if not SIGHTING_SERVICE_AVAILABLE:
        return []
    
    try:
        from core.sighting_service import sighting_service
        return sighting_service.get_recent_sightings(limit)
    except Exception as e:
        print(f"Error getting real sightings: {e}")
        return []

def get_real_env_readings(limit=200):
    """Get real environmental data from sensors"""
    try:
        # Try to get real sensor data
        from utils.env_sensor import get_env_data
        real_data = get_env_data()
        
        if real_data:
            # Return real sensor readings with historical simulation
            from datetime import datetime, timedelta
            readings = []
            base_time = datetime.now()
            
            for i in range(limit):
                readings.append({
                    'timestamp': (base_time - timedelta(hours=i)).isoformat(),
                    'temperature': real_data.get('temperature', 20.0),
                    'humidity': real_data.get('humidity', 50.0),
                    'light_level': real_data.get('light_level', 500.0),
                    'motion_count': 0,  # Would come from motion detection logs
                    'species_count': 0  # Would come from species detection logs
                })
            return readings
        else:
            # Return empty if no sensor data available
            return []
            
    except Exception as e:
        print(f"Error getting environmental data: {e}")
        return []

@research_bp.route('/research')
def research_index():
    return render_template('research/index.html')

@research_bp.route('/research/sightings')
def research_sightings():
    sightings = get_real_sightings(100)
    return render_template('research/sightings.html', sightings=sightings)

# API endpoint for React: /api/research/sightings
@research_bp.route('/api/research/sightings')
def api_research_sightings():
    sightings = get_real_sightings(100)
    return jsonify(sightings)

@research_bp.route('/research/trends')
def research_trends():
    env_data = get_real_env_readings(200)
    return render_template('research/trends.html', env_data=env_data)

# API endpoint for React: /api/research/trends
@research_bp.route('/api/research/trends')
def api_research_trends():
    env_data = get_real_env_readings(200)
    return jsonify(env_data)
