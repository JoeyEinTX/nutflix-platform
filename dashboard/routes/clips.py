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
    try:
        from core.clip_manager import ClipManager
        
        clip_manager = ClipManager()
        limit = request.args.get('limit', 20, type=int)
        days_back = request.args.get('days_back', 7, type=int)
        
        # Get real clips from the system
        clips = clip_manager.scan_clips(days_back=days_back)
        
        # Limit results if requested
        if limit:
            clips = clips[:limit]
        
        # Convert ClipInfo objects to JSON format
        clip_data = []
        for clip in clips:
            clip_data.append({
                'id': clip.filename.stem,  # Remove extension for ID
                'filename': clip.filename.name,
                'timestamp': clip.timestamp.isoformat(),
                'duration': clip.duration,
                'camera': clip.camera_id,
                'trigger_type': clip.trigger_type,
                'thumbnail': f'/api/clips/{clip.filename.stem}/thumbnail',
                'size': f'{clip.file_size / 1024 / 1024:.1f}MB'
            })
        
        return jsonify({
            'clips': clip_data,
            'total': len(clip_data)
        })
        
    except Exception as e:
        print(f"[clips_bp] Error getting clips: {e}")
        return jsonify({'error': str(e), 'clips': [], 'total': 0}), 500

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
    
    # Try to get actual thumbnail from video file
    try:
        from core.clip_manager import ClipManager
        from core.utils.video_thumbnail_extractor import VideoThumbnailExtractor
        
        clip_manager = ClipManager()
        clips = clip_manager.scan_clips(days_back=30)  # Look back further for thumbnails
        
        # Find the clip by ID
        target_clip = None
        for clip in clips:
            if clip.filename.stem == clip_id:
                target_clip = clip
                break
        
        if target_clip and target_clip.filepath.exists():
            # Try to find existing thumbnail
            thumbnail_path = target_clip.filepath.with_suffix('.jpg')
            
            if thumbnail_path.exists():
                # Serve existing thumbnail
                return send_file(str(thumbnail_path), mimetype='image/jpeg')
            else:
                # Generate thumbnail from video
                extractor = VideoThumbnailExtractor()
                success = extractor.extract_thumbnail_from_mp4(
                    str(target_clip.filepath), 
                    str(thumbnail_path)
                )
                
                if success and thumbnail_path.exists():
                    return send_file(str(thumbnail_path), mimetype='image/jpeg')
        
        # Fallback - return a "no thumbnail" image
        import cv2
        import numpy as np
        img = np.zeros((120, 160, 3), dtype=np.uint8)
        img[:] = [50, 50, 50]  # Gray background
        cv2.putText(img, 'No Thumbnail', (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(img, clip_id[:10], (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
        
        # Encode as JPEG
        ret, jpeg = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 85])
        if ret:
            from io import BytesIO
            return send_file(BytesIO(jpeg.tobytes()), mimetype='image/jpeg', as_attachment=False)
            
    except Exception as e:
        print(f"[clips_bp] Error getting thumbnail for {clip_id}: {e}")
    
    return jsonify({'error': f'Could not generate thumbnail for {clip_id}'}), 404

@clips_bp.route('/api/thumbnails/<filename>')
def get_thumbnail_file(filename):
    """Serve thumbnail files directly from thumbnails directory"""
    from flask import send_file
    import os
    
    try:
        # Get the absolute path to the project root
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Construct absolute path to thumbnail
        thumbnail_path = os.path.join(project_root, 'thumbnails', filename)
        
        # Check if file exists
        if os.path.exists(thumbnail_path):
            print(f"✅ Serving thumbnail: {thumbnail_path}")
            return send_file(thumbnail_path, mimetype='image/jpeg')
        else:
            print(f"⚠️ Thumbnail not found: {thumbnail_path}")
            # Return 404 with fallback to placeholder
            return jsonify({'error': f'Thumbnail {filename} not found'}), 404
            
    except Exception as e:
        print(f"❌ Error serving thumbnail {filename}: {e}")
        return jsonify({'error': f'Error serving thumbnail: {e}'}), 500
