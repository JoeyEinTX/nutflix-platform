from flask import Blueprint, render_template, jsonify
# from dashboard.services.analytics import get_recent_sightings, get_recent_env_readings

research_bp = Blueprint('research', __name__, template_folder='../templates/research')

def get_mock_sightings(limit=100):
    """Mock sightings data for development"""
    return [
        {
            'timestamp': '2025-01-23T14:30:00Z',
            'species': 'squirrel',
            'behavior': 'foraging',
            'confidence': 0.92,
            'camera': 'CritterCam',
            'motion_zone': 'feeder_area',
            'clip_path': '/clips/squirrel_001.mp4'
        },
        {
            'timestamp': '2025-01-23T13:15:00Z', 
            'species': 'cardinal',
            'behavior': 'feeding',
            'confidence': 0.87,
            'camera': 'NestCam',
            'motion_zone': 'nest_box',
            'clip_path': '/clips/cardinal_002.mp4'
        },
        {
            'timestamp': '2025-01-23T12:45:00Z',
            'species': 'raccoon',
            'behavior': 'climbing',
            'confidence': 0.95,
            'camera': 'CritterCam', 
            'motion_zone': 'tree_trunk',
            'clip_path': '/clips/raccoon_003.mp4'
        }
    ][:limit]

def get_mock_env_readings(limit=200):
    """Mock environmental data for development"""
    import random
    from datetime import datetime, timedelta
    
    readings = []
    base_time = datetime.now()
    
    for i in range(limit):
        readings.append({
            'timestamp': (base_time - timedelta(hours=i)).isoformat(),
            'temperature': round(20 + random.uniform(-5, 10), 1),
            'humidity': round(45 + random.uniform(-15, 25), 1),
            'light_level': round(random.uniform(0, 1000), 1),
            'motion_count': random.randint(0, 15),
            'species_count': random.randint(0, 5)
        })
    
    return readings

@research_bp.route('/research')
def research_index():
    return render_template('research/index.html')

@research_bp.route('/research/sightings')
def research_sightings():
    sightings = get_mock_sightings(100)
    return render_template('research/sightings.html', sightings=sightings)

# API endpoint for React: /api/research/sightings
@research_bp.route('/api/research/sightings')
def api_research_sightings():
    sightings = get_mock_sightings(100)
    return jsonify(sightings)

@research_bp.route('/research/trends')
def research_trends():
    env_data = get_mock_env_readings(200)
    return render_template('research/trends.html', env_data=env_data)

# API endpoint for React: /api/research/trends
@research_bp.route('/api/research/trends')
def api_research_trends():
    env_data = get_mock_env_readings(200)
    return jsonify(env_data)
