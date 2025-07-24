from flask import Blueprint, render_template, current_app, jsonify, request
import os
from datetime import datetime, timedelta

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

# API endpoints for React app
@clips_bp.route('/api/clips')
def get_clips():
    """Get list of video clips"""
    # Mock data for now - replace with actual file listing later
    mock_clips = [
        {
            'id': 'clip_001',
            'filename': 'squirrel_2025_01_23_14_30.mp4',
            'timestamp': '2025-01-23T14:30:00Z',
            'duration': 45,
            'camera': 'CritterCam',
            'species': 'squirrel',
            'thumbnail': '/api/clips/clip_001/thumbnail',
            'size': '2.3MB'
        },
        {
            'id': 'clip_002', 
            'filename': 'bird_2025_01_23_12_15.mp4',
            'timestamp': '2025-01-23T12:15:00Z',
            'duration': 32,
            'camera': 'NestCam',
            'species': 'cardinal',
            'thumbnail': '/api/clips/clip_002/thumbnail',
            'size': '1.8MB'
        },
        {
            'id': 'clip_003',
            'filename': 'raccoon_2025_01_22_22_45.mp4', 
            'timestamp': '2025-01-22T22:45:00Z',
            'duration': 67,
            'camera': 'CritterCam',
            'species': 'raccoon',
            'thumbnail': '/api/clips/clip_003/thumbnail',
            'size': '3.1MB'
        }
    ]
    
    limit = request.args.get('limit', type=int)
    if limit:
        mock_clips = mock_clips[:limit]
    
    return jsonify({
        'clips': mock_clips,
        'total': len(mock_clips)
    })

@clips_bp.route('/api/clips/<clip_id>')
def get_clip(clip_id):
    """Get specific clip details"""
    return jsonify({
        'id': clip_id,
        'filename': f'{clip_id}.mp4',
        'url': f'/api/clips/{clip_id}/download',
        'thumbnail': f'/api/clips/{clip_id}/thumbnail',
        'metadata': {
            'duration': 45,
            'camera': 'CritterCam',
            'species': 'squirrel',
            'confidence': 0.89
        }
    })

@clips_bp.route('/api/clips/<clip_id>', methods=['DELETE'])
def delete_clip(clip_id):
    """Delete a clip"""
    return jsonify({
        'success': True,
        'message': f'Clip {clip_id} deleted'
    })

@clips_bp.route('/api/clips/<clip_id>/thumbnail')
def get_clip_thumbnail(clip_id):
    """Get thumbnail for a specific clip"""
    from flask import send_file
    import tempfile
    import cv2
    import numpy as np
    
    # For now, generate a mock thumbnail
    # In production, this would extract a frame from the actual video file
    try:
        # Create a mock thumbnail image
        img = np.zeros((120, 160, 3), dtype=np.uint8)
        
        # Different colors/content based on clip type
        if 'squirrel' in clip_id or 'clip_001' in clip_id:
            img[:] = [40, 60, 20]  # Dark green background
            cv2.circle(img, (80, 60), 15, (0, 255, 255), -1)  # Yellow circle (squirrel)
        elif 'bird' in clip_id or 'clip_002' in clip_id:
            img[:] = [60, 40, 40]  # Dark blue background  
            cv2.circle(img, (80, 60), 12, (0, 0, 200), -1)  # Red circle (cardinal)
        elif 'raccoon' in clip_id or 'clip_003' in clip_id:
            img[:] = [30, 30, 30]  # Dark gray background
            cv2.circle(img, (80, 60), 18, (100, 100, 100), -1)  # Gray circle (raccoon)
        else:
            img[:] = [20, 40, 60]  # Default dark background
            cv2.rectangle(img, (70, 50), (90, 70), (255, 255, 255), -1)
        
        # Add timestamp overlay
        cv2.putText(img, '14:30', (5, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        
        # Encode as JPEG
        ret, jpeg = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 85])
        if ret:
            from io import BytesIO
            return send_file(BytesIO(jpeg.tobytes()), mimetype='image/jpeg', as_attachment=False)
    except Exception as e:
        print(f"[clips_bp] Error generating thumbnail for {clip_id}: {e}")
    
    return jsonify({'error': f'Could not generate thumbnail for {clip_id}'}), 404
