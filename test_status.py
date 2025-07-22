#!/usr/bin/env python3
"""Simple test to verify project state"""

import sys
import os
sys.path.insert(0, '.')

print("🐿️ Nutflix Platform - Quick Status Check")
print("=" * 50)

try:
    from core.config.config_manager import get_config
    print("✅ Config manager imported successfully")
    
    config = get_config('nutpod')
    print("✅ NutPod config loaded successfully")
    print(f"📋 Device name: {config.get('device_name')}")
    print(f"📷 Cameras: {config.get('enabled_cameras')}")
    print(f"🎤 Audio: {config.get('record_audio')}")
    
except Exception as e:
    print(f"❌ Config error: {e}")
    import traceback
    traceback.print_exc()

print("\n🔧 Checking other core modules...")
modules = [
    ('camera.camera_manager', 'CameraManager'),
    ('motion.motion_detector', 'MotionDetector'),
    ('audio.audio_recorder', 'AudioRecorder')
]

for module_path, class_name in modules:
    try:
        module = __import__(f'core.{module_path}', fromlist=[class_name])
        cls = getattr(module, class_name)
        print(f"✅ {class_name} available")
    except ImportError as e:
        print(f"❌ {class_name}: Import error - {e}")
    except Exception as e:
        print(f"⚠️  {class_name}: {e}")

print("\n🌐 Testing dashboard...")
try:
    from dashboard.app import app
    print("✅ Dashboard app created")
    print(f"📡 Routes available: {len(list(app.url_map.iter_rules()))}")
except Exception as e:
    print(f"❌ Dashboard error: {e}")

print("\n🎯 Status check complete!")
