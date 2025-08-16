#!/usr/bin/env python3
"""
Auto-fix thumbnails script - runs continuously to link new clips to thumbnails
"""
import sqlite3
import os
import time
import re
from datetime import datetime

def auto_link_thumbnails():
    """Automatically link clips to thumbnails that aren't yet linked"""
    project_root = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(project_root, 'nutflix.db')
    thumbnails_dir = os.path.join(project_root, 'thumbnails')
    
    if not os.path.exists(thumbnails_dir):
        print(f"❌ Thumbnails directory not found: {thumbnails_dir}")
        return
    
    # Get all thumbnail files
    thumbnail_files = [f for f in os.listdir(thumbnails_dir) if f.endswith('_clip.jpg')]
    print(f"Found {len(thumbnail_files)} thumbnail files")
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # Get clips without thumbnail paths
        cursor.execute("""
            SELECT id, camera, clip_path, timestamp 
            FROM clip_metadata 
            WHERE thumbnail_path IS NULL OR thumbnail_path = ''
            ORDER BY timestamp DESC
        """)
        
        clips_to_link = cursor.fetchall()
        linked_count = 0
        
        for clip_id, camera, clip_path, timestamp_str in clips_to_link:
            clip_filename = os.path.basename(clip_path)
            
            # Parse timestamp from clip filename
            # Expected formats: nest_20250803_091322_pir.mp4, crit_20250803_093808_pir.mp4
            match = re.match(r'(nest|crit)_(\d{8})_(\d{6})_.*\.mp4', clip_filename)
            if not match:
                continue
                
            camera_prefix, date_part, time_part = match.groups()
            
            # Convert to thumbnail filename format
            # From: nest_20250803_091322_pir.mp4
            # To: NestCam_2025-08-03_09-13-22_clip.jpg
            camera_name = 'NestCam' if camera_prefix == 'nest' else 'CritterCam'
            formatted_date = f"{date_part[:4]}-{date_part[4:6]}-{date_part[6:8]}"
            formatted_time = f"{time_part[:2]}-{time_part[2:4]}-{time_part[4:6]}"
            
            expected_thumbnail = f"{camera_name}_{formatted_date}_{formatted_time}_clip.jpg"
            
            if expected_thumbnail in thumbnail_files:
                thumbnail_path = f"thumbnails/{expected_thumbnail}"
                
                cursor.execute("""
                    UPDATE clip_metadata 
                    SET thumbnail_path = ? 
                    WHERE id = ?
                """, (thumbnail_path, clip_id))
                
                print(f"✅ Linked {clip_filename} -> {expected_thumbnail}")
                linked_count += 1
        
        if linked_count > 0:
            conn.commit()
            print(f"🎉 Linked {linked_count} new clips to thumbnails")
        else:
            print("ℹ️ No new clips to link")

if __name__ == '__main__':
    print(f"🔧 Auto-thumbnail linking started at {datetime.now()}")
    auto_link_thumbnails()
