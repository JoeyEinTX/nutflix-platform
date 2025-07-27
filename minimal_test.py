#!/usr/bin/env python3
"""
Minimal import test
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing core imports...")

try:
    print("1. Testing clip_manager...")
    from core.clip_manager import ClipManager
    print("✅ ClipManager imported")
    
    print("2. Testing motion_event_handler...")  
    from core.motion_event_handler import MotionEventHandler
    print("✅ MotionEventHandler imported")
    
    print("3. Testing recording_engine...")
    from core.recording_engine import RecordingEngine
    print("✅ RecordingEngine imported")
    
except Exception as e:
    print(f"❌ Import failed: {e}")
    import traceback
    traceback.print_exc()

print("Done!")
