#!/usr/bin/env python3
"""
Simple test of the clip recording system without camera conflicts
"""

import os
import sys
import logging
import time
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

print("🎬 Simple Clip Recording Test")
print("=" * 40)

try:
    # Test basic imports
    print("📦 Testing imports...")
    from core.recording_engine import RecordingEngine
    from core.clip_manager import ClipManager  
    from core.motion_event_handler import MotionEventHandler
    print("✅ All imports successful")
    
    # Create mock settings
    class MockSettings:
        def get(self, key, default=None):
            return {
                'clip_settings': {
                    'enabled': True,  
                    'duration_seconds': 3.0,
                    'storage_path': './test_clips',
                    'max_clips': 5,
                    'record_on_motion': {'nestcam': True, 'crittercam': True}
                }
            }.get(key, default)
    
    print("⚙️ Creating components...")
    settings = MockSettings()
    
    # Test ClipManager (safest component)
    clip_manager = ClipManager(settings)
    print("✅ ClipManager created")
    
    # Test storage stats
    stats = clip_manager.get_storage_stats()
    print(f"📊 Storage: {stats['total_clips']} clips, {stats['total_size_mb']:.1f} MB")
    
    # Test MotionEventHandler (doesn't init cameras directly)
    print("🚨 Testing MotionEventHandler...")
    motion_handler = MotionEventHandler(settings)
    print("✅ MotionEventHandler created")
    
    # Test motion statistics
    stats = motion_handler.get_motion_statistics()
    print(f"📈 Motion stats: {stats['total_motion_events']} events")
    
    print("\n🎉 Basic component test passed!")
    print("🔧 System is ready for integration")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n👋 Test complete")
