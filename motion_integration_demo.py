#!/usr/bin/env python3
"""
Nutflix Lite - Motion Integration Example

Shows how to integrate the clip recording system with existing motion detection.
This example demonstrates the complete flow without conflicting with other camera users.
"""

import os
import sys
import time
import logging
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.motion_event_handler import create_motion_recording_system

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DemoSettings:
    """Demo settings that mimic the YAML settings structure"""
    
    def get(self, key, default=None):
        settings = {
            'clip_settings': {
                'enabled': True,
                'duration_seconds': 8.0,  # 8 second clips
                'storage_path': './nutflix_clips',
                'max_clips': 50,
                'max_age_days': 14,
                'enable_ir_at_night': True,
                'ir_gpio_pin': 23,
                'record_on_motion': {
                    'nestcam': True,
                    'crittercam': True
                },
                'organize_by_camera': True,
                'organize_by_date': True,
                'cooldown_seconds': 3.0
            }
        }
        return settings.get(key, default)

def motion_callback(camera_name: str, timestamp: str):
    """
    Motion detection callback - this is what your existing motion detector should call
    """
    logger.info(f"🎯 Motion detected on {camera_name} at {timestamp}")
    
    # The motion event handler will automatically trigger recording
    # This is already handled by registering the handler with the motion detector

def main():
    print("\n" + "="*60)
    print("🎥 NUTFLIX LITE - MOTION RECORDING INTEGRATION") 
    print("="*60)
    print("This demonstrates how to integrate clip recording with motion detection")
    print("-"*60)
    
    # Create settings
    settings = DemoSettings()
    
    # Create the motion recording system
    # In real usage, you'd pass your actual motion detector here
    motion_handler = create_motion_recording_system(settings_manager=settings)
    
    print(f"\n✅ Motion recording system initialized")
    print(f"📁 Storage: {settings.get('clip_settings')['storage_path']}")
    print(f"⏱️  Clip duration: {settings.get('clip_settings')['duration_seconds']}s")
    print(f"🔄 Cooldown: {settings.get('clip_settings')['cooldown_seconds']}s")
    
    # Show initial statistics
    stats = motion_handler.get_motion_statistics()
    print(f"\n📊 Initial Statistics:")
    print(f"   Motion events: {stats['total_motion_events']}")
    print(f"   Recordings triggered: {stats['recordings_triggered']}")
    print(f"   Success rate: {stats['success_rate']:.1f}%")
    
    # Simulate some motion events
    print(f"\n🎭 Simulating motion detection events...")
    
    test_events = [
        ("NestCam", "Wildlife detected"),
        ("CritterCam", "Movement in frame"), 
        ("NestCam", "Should be in cooldown"),  # This should be skipped
        ("CritterCam", "Another critter"),
    ]
    
    for i, (camera, description) in enumerate(test_events):
        print(f"\n{i+1}. 🚨 Simulating: {camera} - {description}")
        
        # Generate timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Trigger motion event (this is what your motion detector would do)
        success = motion_handler.handle_motion_event(camera, timestamp)
        
        if success:
            print(f"   ✅ Recording triggered for {camera}")
        else:
            print(f"   ⏭️  Recording skipped for {camera}")
        
        # Show current stats
        current_stats = motion_handler.get_motion_statistics()
        print(f"   📈 Stats: {current_stats['total_motion_events']} events, "
              f"{current_stats['recordings_triggered']} recordings, "
              f"{current_stats['recordings_skipped_cooldown']} cooldown skips")
        
        # Wait a bit between events
        time.sleep(2)
    
    # Wait for recordings to complete
    print(f"\n⏳ Waiting for recordings to complete...")
    time.sleep(10)
    
    # Final statistics
    final_stats = motion_handler.get_motion_statistics()
    print(f"\n📊 Final Statistics:")
    print(f"   Total motion events: {final_stats['total_motion_events']}")
    print(f"   Recordings triggered: {final_stats['recordings_triggered']}")
    print(f"   Skipped (cooldown): {final_stats['recordings_skipped_cooldown']}")
    print(f"   Skipped (disabled): {final_stats['recordings_skipped_disabled']}")
    print(f"   Success rate: {final_stats['success_rate']:.1f}%")
    
    # Check storage
    storage_stats = motion_handler.clip_manager.get_storage_stats()
    print(f"\n💾 Storage Status:")
    print(f"   Total clips: {storage_stats['total_clips']}")
    print(f"   Storage used: {storage_stats['total_size_mb']:.1f} MB")
    print(f"   Storage path: {storage_stats['storage_path']}")
    
    if storage_stats['total_clips'] > 0:
        print(f"\n📁 Camera breakdown:")
        for camera, stats in storage_stats.get('camera_breakdown', {}).items():
            print(f"   {camera}: {stats['count']} clips ({stats['size']/1024:.1f} KB)")
    
    # Show recent clips
    recent_clips = motion_handler.get_recent_clips(limit=5)
    if recent_clips:
        print(f"\n📄 Recent clips:")
        for clip in recent_clips:
            print(f"   📹 {clip.camera_id}: {Path(clip.filename).name}")
            print(f"      Size: {clip.file_size/1024:.1f} KB, Trigger: {clip.trigger_type}")
            print(f"      Time: {clip.timestamp.strftime('%H:%M:%S')}")
    
    print(f"\n" + "="*60)
    print(f"🎉 INTEGRATION DEMO COMPLETE!")
    print(f"="*60)
    print(f"✅ Motion recording system is working")
    print(f"🔧 Ready to integrate with your existing motion detector")
    print(f"📚 Next steps:")
    print(f"   1. Import: from core.motion_event_handler import create_motion_recording_system")
    print(f"   2. Create: motion_handler = create_motion_recording_system(your_settings, your_motion_detector)")
    print(f"   3. The system will automatically record clips when motion is detected")
    
    # Cleanup prompt
    response = input(f"\n🧹 Clean up test clips? (y/N): ").strip().lower()
    if response == 'y':
        clips_path = Path(settings.get('clip_settings')['storage_path'])
        if clips_path.exists():
            import shutil
            shutil.rmtree(clips_path)
            print(f"✅ Test clips cleaned up")
    
    print(f"\n👋 Demo finished")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n⛔ Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        import traceback
        traceback.print_exc()
