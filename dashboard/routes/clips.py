from flask import Blueprint, render_template, current_app, jsonify, request
import os
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

clips_bp = Blueprint('clips', __name__)

# Database path
DB_PATH = '/home/p12146/Projects/Nutflix-platform/nutflix.db'

@clips_bp.route('/')
def index():
    """Legacy clips page"""
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
    """Get list of PIR-triggered video clips from database"""
    try:
        limit = request.args.get('limit', 20, type=int)
        camera_filter = request.args.get('camera', None)
        
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        # Query clips from database
        if camera_filter:
            cur.execute('''
                SELECT id, timestamp, camera, clip_path, thumbnail_path, duration, 
                       trigger_type, has_audio, species, behavior, confidence, created_at
                FROM clip_metadata 
                WHERE camera = ?
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (camera_filter, limit))
        else:
            cur.execute('''
                SELECT id, timestamp, camera, clip_path, thumbnail_path, duration, 
                       trigger_type, has_audio, species, behavior, confidence, created_at
                FROM clip_metadata 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (limit,))
        
        clips = cur.fetchall()
        conn.close()
        
        # Convert database results to JSON format
        clip_data = []
        for clip in clips:
            (clip_id, timestamp, camera, clip_path, thumbnail_path, duration, 
             trigger_type, has_audio, species, behavior, confidence, created_at) = clip
            
            # Calculate file size if file exists
            file_size = 0
            if clip_path:
                full_path = Path('/home/p12146/Projects/Nutflix-platform') / clip_path.lstrip('/')
                if full_path.exists():
                    file_size = full_path.stat().st_size
            
            clip_data.append({
                'id': clip_id,
                'filename': Path(clip_path).name if clip_path else 'unknown.mp4',
                'timestamp': timestamp,
                'duration': duration or 0,
                'camera': camera,
                'trigger_type': trigger_type or 'pir_motion',
                'has_audio': bool(has_audio),
                'species': species or 'Wildlife',
                'behavior': behavior or 'investigating',
                'confidence': confidence or 0.95,
                'thumbnail': thumbnail_path,
                'video_url': clip_path,
                'size': f'{file_size / 1024 / 1024:.1f}MB' if file_size > 0 else '0MB',
                'created_at': created_at
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

@clips_bp.route('/api/clip_thumbnail/<camera_id>')
def get_latest_clip_thumbnail(camera_id):
    """Get thumbnail for the latest clip from a specific camera"""
    from flask import send_file, redirect, url_for
    import sqlite3
    import os
    
    try:
        print(f"🔍 Thumbnail request for camera_id: {camera_id}")
        
        # Map frontend camera IDs to backend camera names
        camera_name_map = {
            'camera-1': 'NestCam', 'camera-3': 'NestCam', 'camera-5': 'NestCam',
            'camera-2': 'CritterCam', 'camera-4': 'CritterCam', 'camera-6': 'CritterCam'
        }
        
        real_camera_name = camera_name_map.get(camera_id)
        if not real_camera_name:
            print(f"⚠️ Unknown camera_id: {camera_id}")
            return jsonify({'error': f'Unknown camera {camera_id}'}), 404
        
        # Connect to database and get latest clip for this camera
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        db_path = os.path.join(project_root, 'nutflix.db')
        
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Get the latest clip for this camera
            cursor.execute("""
                SELECT thumbnail_path, clip_path, timestamp 
                FROM clip_metadata 
                WHERE camera = ? 
                ORDER BY timestamp DESC 
                LIMIT 1
            """, (real_camera_name,))
            
            result = cursor.fetchone()
            
            if result and result[0]:  # If we have a thumbnail_path
                thumbnail_path = result[0]
                
                # Convert to absolute path
                if not os.path.isabs(thumbnail_path):
                    full_thumbnail_path = os.path.join(project_root, thumbnail_path)
                else:
                    full_thumbnail_path = thumbnail_path
                
                # Check if thumbnail file exists
                if os.path.exists(full_thumbnail_path):
                    print(f"✅ Serving thumbnail: {full_thumbnail_path}")
                    return send_file(full_thumbnail_path, mimetype='image/jpeg')
                else:
                    print(f"⚠️ Thumbnail not found: {full_thumbnail_path}")
                    
                    # Try to find thumbnail in thumbnails directory by filename pattern
                    if result[1]:  # If we have clip_path
                        clip_filename = os.path.basename(result[1])
                        # Convert clip filename to thumbnail filename
                        if clip_filename.endswith('.mp4'):
                            thumbnail_filename = clip_filename.replace('.mp4', '_clip.jpg')
                            thumbnail_in_dir = os.path.join(project_root, 'thumbnails', thumbnail_filename)
                            
                            if os.path.exists(thumbnail_in_dir):
                                print(f"✅ Found thumbnail in thumbnails dir: {thumbnail_in_dir}")
                                return send_file(thumbnail_in_dir, mimetype='image/jpeg')
            
            # If no thumbnail found, redirect to live camera thumbnail
            print(f"🔄 Redirecting to live thumbnail: /api/stream/{real_camera_name}/thumbnail")
            return redirect(f"/api/stream/{real_camera_name}/thumbnail")
            
    except Exception as e:
        print(f"❌ Error getting thumbnail for {camera_id}: {e}")
        # Fallback to live thumbnail
        camera_name_map = {
            'camera-1': 'NestCam', 'camera-3': 'NestCam', 'camera-5': 'NestCam',
            'camera-2': 'CritterCam', 'camera-4': 'CritterCam', 'camera-6': 'CritterCam'
        }
        real_camera_name = camera_name_map.get(camera_id, 'NestCam')
        return redirect(f"/api/stream/{real_camera_name}/thumbnail")

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
