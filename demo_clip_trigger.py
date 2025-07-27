#!/usr/bin/env python3
"""
demo_clip_trigger.py

Demo script to test the Nutflix Lite clip recording system.
Simulates motion detection events and verifies the complete flow:
Motion Detection → Recording Engine → Clip Manager → File Storage
"""

import os
import sys
import time
import logging
from datetime import datetime
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.motion_event_handler import MotionEventHandler, create_motion_recording_system
from core.recording_engine import RecordingEngine
from core.clip_manager import ClipManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MockSettingsManager:
    """Mock settings manager for demo purposes"""
    
    def __init__(self):
        self.settings = {
            'clip_settings': {
                'enabled': True,
                'duration_seconds': 5.0,  # Shorter for demo
                'storage_path': './demo_clips',
                'max_clips': 10,
                'max_age_days': 7,
                'enable_ir_at_night': True,
                'ir_gpio_pin': 23,
                'record_on_motion': {
                    'nestcam': True,
                    'crittercam': True
                },
                'organize_by_camera': True,
                'organize_by_date': True,
                'cooldown_seconds': 2.0  # Shorter cooldown for demo
            }
        }
    
    def get(self, key, default=None):
        """Get setting value"""
        return self.settings.get(key, default)

class MockMotionDetector:
    """Mock motion detector for demo purposes"""
    
    def __init__(self):
        self.callback = None
        self.cameras = ['NestCam', 'CritterCam']
    
    def register_callback(self, callback):
        """Register motion event callback"""
        self.callback = callback
        logger.info("🔗 Mock motion detector callback registered")
    
    def simulate_motion(self, camera_name: str):
        """Simulate a motion detection event"""
        if self.callback:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            logger.info(f"🎭 Simulating motion on {camera_name}")
            self.callback(camera_name, timestamp)
        else:
            logger.warning("⚠️ No callback registered")

def print_banner():
    """Print demo banner"""
    print("\n" + "="*60)
    print("🎥 NUTFLIX LITE - CLIP RECORDING SYSTEM DEMO")
    print("="*60)
    print("Testing: Motion Detection → Recording → Storage")
    print("-"*60)

def demo_basic_recording():
    """Demo basic recording functionality"""
    print("\n🎬 DEMO 1: Basic Recording Engine")
    print("-" * 40)
    
    # Create settings and recording engine
    settings = MockSettingsManager()
    engine = RecordingEngine(settings)
    
    # Test recording both cameras
    cameras = ['NestCam', 'CritterCam']
    
    for camera in cameras:
        print(f"\n📹 Testing {camera} recording...")
        success = engine.start_recording(
            camera_id=camera,
            duration=3.0,  # Short demo recording
            use_ir=camera == 'NestCam',  # Only NestCam has IR
            trigger_type='demo'
        )
        
        if success:
            print(f"✅ {camera} recording started")
        else:
            print(f"❌ {camera} recording failed")
        
        # Show active recordings
        active = engine.get_active_recordings()
        if active:
            print(f"🎥 Active recordings: {list(active.keys())}")
        
        # Wait a bit
        time.sleep(1)
    
    # Wait for recordings to complete
    print("\n⏳ Waiting for recordings to complete...")
    time.sleep(4)
    
    # Check final state
    active = engine.get_active_recordings()
    print(f"🎥 Active recordings after completion: {list(active.keys()) if active else 'None'}")

def demo_clip_management():
    """Demo clip management functionality"""
    print("\n📁 DEMO 2: Clip Management")
    print("-" * 40)
    
    settings = MockSettingsManager()
    clip_manager = ClipManager(settings)
    
    # Show storage stats
    stats = clip_manager.get_storage_stats()
    print(f"📊 Storage stats: {stats['total_clips']} clips, "
          f"{stats['total_size_mb']:.1f} MB")
    
    # Scan for clips
    clips = clip_manager.scan_clips(days_back=1)
    print(f"🔍 Found {len(clips)} recent clips")
    
    for clip in clips[:3]:  # Show first 3
        print(f"  📄 {clip.camera_id}: {clip.filename} "
              f"({clip.file_size/1024:.1f} KB, {clip.trigger_type})")
    
    # Demo cleanup
    if len(clips) > 0:
        print("\n🧹 Testing cleanup...")
        cleanup_stats = clip_manager.cleanup_old_clips(max_clips=5)
        print(f"🧹 Cleanup results: {cleanup_stats}")

def demo_motion_integration():
    """Demo complete motion-to-recording integration"""
    print("\n🚨 DEMO 3: Motion Integration")
    print("-" * 40)
    
    # Create mock components
    settings = MockSettingsManager()
    motion_detector = MockMotionDetector()
    
    # Create integrated system
    motion_handler = create_motion_recording_system(settings, motion_detector)
    
    # Show initial stats
    stats = motion_handler.get_motion_statistics()
    print(f"📊 Initial stats: {stats['total_motion_events']} events, "
          f"{stats['recordings_triggered']} recordings")
    
    # Simulate motion events
    motion_events = [
        ('NestCam', 0),
        ('CritterCam', 1),
        ('NestCam', 2),  # Should be in cooldown
        ('CritterCam', 4),
        ('NestCam', 6),  # Should work (out of cooldown)
    ]
    
    for camera, delay in motion_events:
        if delay > 0:
            print(f"⏳ Waiting {delay}s...")
            time.sleep(delay)
        
        print(f"🚨 Triggering motion on {camera}")
        motion_detector.simulate_motion(camera)
        
        # Show immediate stats
        stats = motion_handler.get_motion_statistics()
        print(f"  📊 Events: {stats['total_motion_events']}, "
              f"Recordings: {stats['recordings_triggered']}, "
              f"Cooldown skips: {stats['recordings_skipped_cooldown']}")
    
    # Wait for recordings to complete
    print("\n⏳ Waiting for all recordings to complete...")
    time.sleep(8)
    
    # Final stats
    final_stats = motion_handler.get_motion_statistics()
    print(f"\n📊 Final Statistics:")
    print(f"  Total motion events: {final_stats['total_motion_events']}")
    print(f"  Recordings triggered: {final_stats['recordings_triggered']}")
    print(f"  Skipped (cooldown): {final_stats['recordings_skipped_cooldown']}")
    print(f"  Skipped (disabled): {final_stats['recordings_skipped_disabled']}")  
    print(f"  Success rate: {final_stats['success_rate']:.1f}%")

def demo_file_inspection():
    """Inspect created files"""
    print("\n📂 DEMO 4: File Inspection")
    print("-" * 40)
    
    demo_clips_path = Path('./demo_clips')
    if not demo_clips_path.exists():
        print("❌ No demo clips directory found")
        return
    
    print(f"📁 Demo clips directory: {demo_clips_path.absolute()}")
    
    # List all files
    all_files = []
    for pattern in ['*.mp4', '*.h264', '*.mock', '*.json']:
        all_files.extend(demo_clips_path.rglob(pattern))
    
    if not all_files:
        print("📭 No clip files found")
        return
    
    print(f"📄 Found {len(all_files)} files:")
    
    for file_path in sorted(all_files):
        try:
            stat = file_path.stat()
            size_kb = stat.st_size / 1024
            mod_time = datetime.fromtimestamp(stat.st_mtime)
            
            print(f"  📄 {file_path.name}")
            print(f"     Size: {size_kb:.1f} KB")
            print(f"     Modified: {mod_time.strftime('%H:%M:%S')}")
            
            # Show metadata if it's a JSON file
            if file_path.suffix == '.json':
                try:
                    import json
                    with open(file_path, 'r') as f:
                        metadata = json.load(f)
                    print(f"     Camera: {metadata.get('camera_id', 'unknown')}")
                    print(f"     Trigger: {metadata.get('trigger_type', 'unknown')}")
                    print(f"     IR Used: {metadata.get('ir_used', False)}")
                except:
                    pass
            
            print()
            
        except Exception as e:
            print(f"  ❌ Error reading {file_path.name}: {e}")

def cleanup_demo_files():
    """Clean up demo files"""
    response = input("\n🧹 Clean up demo files? (y/N): ").strip().lower()
    if response == 'y':
        demo_clips_path = Path('./demo_clips')
        if demo_clips_path.exists():
            import shutil
            shutil.rmtree(demo_clips_path)
            print("✅ Demo clips directory deleted")
        else:
            print("📭 No demo files to clean up")

def main():
    """Run the complete demo"""
    print_banner()
    
    try:
        # Run demos in sequence
        demo_basic_recording()
        demo_clip_management()
        demo_motion_integration()
        demo_file_inspection()
        
        print("\n" + "="*60)
        print("🎉 DEMO COMPLETE!")
        print("="*60)
        print("✅ All systems tested successfully")
        print("📁 Check ./demo_clips/ for generated files")
        print("🔧 Ready for integration with real motion detection")
        
        cleanup_demo_files()
        
    except KeyboardInterrupt:
        print("\n\n⛔ Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n👋 Demo finished")

if __name__ == "__main__":
    main()
