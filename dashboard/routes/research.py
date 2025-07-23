from flask import Blueprint, render_template, jsonify
from dashboard.services.analytics import get_recent_sightings, get_recent_env_readings

research_bp = Blueprint('research', __name__, template_folder='../templates/research')

@research_bp.route('/research')
def research_index():
    return render_template('research/index.html')

@research_bp.route('/research/sightings')
def research_sightings():
    sightings = get_recent_sightings(100)
    return render_template('research/sightings.html', sightings=sightings)

# API endpoint for React: /api/research/sightings
@research_bp.route('/api/research/sightings')
def api_research_sightings():
    sightings = get_recent_sightings(100)
    return jsonify(sightings)

@research_bp.route('/research/trends')
def research_trends():
    env_data = get_recent_env_readings(200)
    return render_template('research/trends.html', env_data=env_data)

# API endpoint for React: /api/research/trends
@research_bp.route('/api/research/trends')
def api_research_trends():
    env_data = get_recent_env_readings(200)
    return jsonify(env_data)
