#!/usr/bin/env python3
"""
Test the complete motion detection -> recording -> thumbnail workflow
"""

import os
import sys
import time
import json
from datetime import datetime
from pathlib import Path

# Add the project root to Python path
sys.path.append('/home/p12146/NutFlix/nutflix-platform')

def test_complete_workflow():
    """Test the complete workflow from motion detection to thumbnail creation"""
    
    print("🧪 Testing Complete Motion Detection Workflow")
    print("=" * 60)
    
    try:
        # Import components
        from core.recording_engine import RecordingEngine
        from core.utils.video_thumbnail_extractor import VideoThumbnailExtractor
        from core.sighting_service import SightingService
        from core.camera.mock_camera_manager import MockCameraManager
        
        print("✅ All imports successful")
        
        # Initialize components
        mock_camera_manager = MockCameraManager()
        recording_engine = RecordingEngine()
        video_extractor = VideoThumbnailExtractor()
        sighting_service = SightingService(mock_camera_manager)
        
        print("✅ All components initialized")
        
        # Test 1: Create a mock recording
        print("\n📹 Test 1: Creating mock video recording...")
        
        camera_id = "CritterCam"
        duration = 3.0  # Short duration for testing
        
        success = recording_engine.start_recording(
            camera_id=camera_id,
            duration=duration,
            trigger_type="motion"
        )
        
        if success:
            print(f"✅ Recording started for {camera_id}")
            
            # Wait for recording to complete (plus buffer)
            time.sleep(duration + 2)
            
            # Check for generated clips
            clips_dir = Path("./clips")
            if clips_dir.exists():
                clip_files = list(clips_dir.glob("*.mp4")) + list(clips_dir.glob("*.mock"))
                metadata_files = list(clips_dir.glob("*.json"))
                
                print(f"📁 Found {len(clip_files)} clip files")
                print(f"📄 Found {len(metadata_files)} metadata files")
                
                if clip_files:
                    latest_clip = max(clip_files, key=lambda x: x.stat().st_mtime)
                    print(f"📹 Latest clip: {latest_clip.name}")
                    
                    # Look for corresponding metadata
                    metadata_file = latest_clip.with_suffix(latest_clip.suffix + ".json")
                    if metadata_file.exists():
                        print(f"📄 Found metadata: {metadata_file.name}")
                        
                        with open(metadata_file, 'r') as f:
                            metadata = json.load(f)
                        
                        print("📊 Recording metadata:")
                        for key, value in metadata.items():
                            print(f"   {key}: {value}")
                        
                        # Test 2: Create sighting from recording
                        print("\n🎯 Test 2: Creating sighting from recording...")
                        
                        sighting = sighting_service.create_sighting_from_recording(camera_id, metadata)
                        
                        if sighting:
                            print("✅ Sighting created successfully!")
                            print("🐿️ Sighting details:")
                            for key, value in sighting.items():
                                print(f"   {key}: {value}")
                            
                            # Test 3: Check thumbnail creation
                            print("\n📸 Test 3: Checking thumbnail creation...")
                            
                            thumbnail_path = metadata.get('thumbnail_path')
                            if thumbnail_path and Path(thumbnail_path).exists():
                                print(f"✅ Thumbnail found: {thumbnail_path}")
                                
                                # Check thumbnail size
                                thumb_size = Path(thumbnail_path).stat().st_size
                                print(f"📏 Thumbnail size: {thumb_size} bytes")
                                
                            else:
                                print("⚠️ No thumbnail found, attempting manual extraction...")
                                
                                # Try to extract thumbnail manually
                                thumbnail_path = video_extractor.extract_thumbnail_from_video(
                                    str(latest_clip),
                                    metadata.get('start_time'),
                                    camera_id
                                )
                                
                                if thumbnail_path:
                                    print(f"✅ Manual thumbnail extraction successful: {thumbnail_path}")
                                else:
                                    print("❌ Manual thumbnail extraction failed")
                        else:
                            print("❌ Failed to create sighting from recording")
                    else:
                        print("⚠️ No metadata file found")
                else:
                    print("⚠️ No clip files found")
            else:
                print("⚠️ Clips directory not found")
        else:
            print("❌ Failed to start recording")
        
        # Test 4: Check recent sightings
        print("\n📋 Test 4: Checking recent sightings...")
        
        recent_sightings = sighting_service.get_recent_sightings(limit=5)
        
        if recent_sightings:
            print(f"✅ Found {len(recent_sightings)} recent sightings")
            for i, sighting in enumerate(recent_sightings, 1):
                species = sighting.get('species', 'Unknown')
                timestamp = sighting.get('timestamp', 'Unknown')
                camera = sighting.get('camera', 'Unknown')
                thumbnail = sighting.get('thumbnail_path', 'None')
                print(f"   {i}. {species} on {camera} at {timestamp} (thumbnail: {thumbnail})")
        else:
            print("⚠️ No recent sightings found")
        
        # Test 5: Test thumbnail serving
        print("\n🌐 Test 5: Testing thumbnail serving...")
        
        thumbnails_dir = Path("./thumbnails")
        if thumbnails_dir.exists():
            thumbnail_files = list(thumbnails_dir.glob("*.jpg"))
            print(f"📸 Found {len(thumbnail_files)} thumbnail files in thumbnails directory")
            
            for thumb_file in thumbnail_files[-3:]:  # Show last 3
                size = thumb_file.stat().st_size
                mtime = datetime.fromtimestamp(thumb_file.stat().st_mtime)
                print(f"   📸 {thumb_file.name} ({size} bytes, {mtime.strftime('%H:%M:%S')})")
        else:
            print("⚠️ Thumbnails directory not found")
        
        print("\n✅ Workflow testing complete!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_complete_workflow()
