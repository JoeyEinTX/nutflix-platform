#!/usr/bin/env python3
"""
Fix thumbnail paths in the database by linking existing thumbnails to clips
"""

import sqlite3
import os
import re
from pathlib import Path

def fix_thumbnail_paths():
    # Get project root
    project_root = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(project_root, 'nutflix.db')
    thumbnails_dir = os.path.join(project_root, 'thumbnails')
    
    # Get all thumbnail files
    thumbnail_files = []
    if os.path.exists(thumbnails_dir):
        for file in os.listdir(thumbnails_dir):
            if file.endswith('.jpg'):
                thumbnail_files.append(file)
    
    print(f"Found {len(thumbnail_files)} thumbnail files")
    
    # Connect to database
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # Get all clips
        cursor.execute("SELECT id, clip_path, timestamp FROM clip_metadata")
        clips = cursor.fetchall()
        
        updated_count = 0
        
        for clip_id, clip_path, timestamp in clips:
            if not clip_path:
                continue
                
            # Extract filename from clip path
            clip_filename = os.path.basename(clip_path)
            
            # Convert clip filename to expected thumbnail format
            # From: nest_20250803_090431_pir.mp4  
            # To: NestCam_2025-08-03_09-04-31_clip.jpg
            
            if clip_filename.startswith('nest_'):
                # NestCam clips
                match = re.match(r'nest_(\d{8})_(\d{6})_.*\.mp4', clip_filename)
                if match:
                    date_str = match.group(1)  # 20250803
                    time_str = match.group(2)  # 090431
                    
                    # Format date: 20250803 -> 2025-08-03
                    formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
                    
                    # Format time: 090431 -> 09-04-31
                    formatted_time = f"{time_str[:2]}-{time_str[2:4]}-{time_str[4:6]}"
                    
                    expected_thumbnail = f"NestCam_{formatted_date}_{formatted_time}_clip.jpg"
                    
            elif clip_filename.startswith('crit_'):
                # CritterCam clips
                match = re.match(r'crit_(\d{8})_(\d{6})_.*\.mp4', clip_filename)
                if match:
                    date_str = match.group(1)  # 20250802
                    time_str = match.group(2)  # 232909
                    
                    # Format date: 20250802 -> 2025-08-02
                    formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
                    
                    # Format time: 232909 -> 23-29-09
                    formatted_time = f"{time_str[:2]}-{time_str[2:4]}-{time_str[4:6]}"
                    
                    expected_thumbnail = f"CritterCam_{formatted_date}_{formatted_time}_clip.jpg"
            else:
                continue
            
            # Check if expected thumbnail exists
            if expected_thumbnail in thumbnail_files:
                thumbnail_path = f"thumbnails/{expected_thumbnail}"
                
                # Update database
                cursor.execute(
                    "UPDATE clip_metadata SET thumbnail_path = ? WHERE id = ?",
                    (thumbnail_path, clip_id)
                )
                
                print(f"✅ Linked {clip_filename} -> {expected_thumbnail}")
                updated_count += 1
            else:
                print(f"⚠️ No thumbnail found for {clip_filename} (expected: {expected_thumbnail})")
        
        conn.commit()
        print(f"\n🎉 Updated {updated_count} clips with thumbnail paths")

if __name__ == "__main__":
    fix_thumbnail_paths()
