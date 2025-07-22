#!/usr/bin/env python3
"""
Nutflix Platform - Comprehensive Debug Test
Run this to systematically test all components
"""

import sys
import os
import logging
import time
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler('logs/debug_test.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('debug_test')

def test_imports():
    """Test all core module imports"""
    print("\n🧪 Testing Module Imports")
    print("=" * 50)
    
    modules = {
        'Config Manager': 'core.config.config_manager',
        'Camera Manager': 'core.camera.camera_manager',
        'Motion Detector': 'core.motion.motion_detector', 
        'Recording Engine': 'core.recording.recording_engine',
        'Stream Server': 'core.stream.stream_server',
        'Audio Recorder': 'core.audio.audio_recorder',
        'File Manager': 'core.storage.file_manager',
        'Dashboard': 'dashboard.app'
    }
    
    results = {}
    for name, module in modules.items():
        try:
            __import__(module)
            print(f"✅ {name}")
            results[name] = True
        except ImportError as e:
            print(f"❌ {name}: Import Error - {e}")
            results[name] = False
        except Exception as e:
            print(f"⚠️  {name}: {e}")
            results[name] = False
    
    return results

def test_config():
    """Test configuration loading"""
    print("\n⚙️  Testing Configuration")
    print("=" * 50)
    
    try:
        from core.config.config_manager import get_config
        
        # Test each device config
        devices = ['nutpod', 'scoutpod', 'groundpod']
        for device in devices:
            try:
                config = get_config(device)
                print(f"✅ {device} config loaded: {len(config)} keys")
            except Exception as e:
                print(f"❌ {device} config failed: {e}")
                
    except Exception as e:
        print(f"❌ Config manager failed: {e}")

def test_hardware_detection():
    """Test hardware detection"""
    print("\n🔧 Testing Hardware Detection")
    print("=" * 50)
    
    # Check video devices
    video_devices = list(Path('/dev').glob('video*'))
    if video_devices:
        print(f"✅ Found {len(video_devices)} video device(s):")
        for dev in video_devices:
            print(f"   📷 {dev}")
    else:
        print("❌ No video devices found")
    
    # Check audio devices
    try:
        import sounddevice as sd
        devices = sd.query_devices()
        audio_devices = [d for d in devices if d['max_input_channels'] > 0]
        if audio_devices:
            print(f"✅ Found {len(audio_devices)} audio input device(s)")
            for i, dev in enumerate(audio_devices):
                print(f"   🎤 {i}: {dev['name']}")
        else:
            print("❌ No audio input devices found")
    except ImportError:
        print("⚠️  sounddevice not available - can't check audio")
    except Exception as e:
        print(f"❌ Audio check failed: {e}")

def test_camera_init():
    """Test camera initialization"""
    print("\n📷 Testing Camera Initialization")
    print("=" * 50)
    
    try:
        from core.camera.camera_manager import CameraManager
        cam_mgr = CameraManager("nutpod")
        print("✅ Camera manager created successfully")
        
        # Try to get camera info without starting
        try:
            cameras = cam_mgr.get_available_cameras()
            print(f"✅ Found {len(cameras)} available cameras")
        except Exception as e:
            print(f"⚠️  Camera detection failed: {e}")
            
    except Exception as e:
        print(f"❌ Camera manager failed: {e}")

def test_motion_detector():
    """Test motion detector initialization"""
    print("\n🏃 Testing Motion Detector")
    print("=" * 50)
    
    try:
        from core.motion.motion_detector import MotionDetector
        
        # Test with dummy pins
        test_pins = {"TestCamera": 18}
        
        def dummy_callback(camera_name, timestamp):
            print(f"📍 Motion callback: {camera_name} at {timestamp}")
        
        motion = MotionDetector(test_pins, callback=dummy_callback, debounce_sec=1.0)
        print("✅ Motion detector created successfully")
        
        # Don't actually start it in test mode
        
    except Exception as e:
        print(f"❌ Motion detector failed: {e}")

def test_flask_dashboard():
    """Test Flask dashboard"""
    print("\n🌐 Testing Dashboard")
    print("=" * 50)
    
    try:
        from dashboard.app import app
        print("✅ Dashboard app created successfully")
        
        # Test that routes are registered
        routes = [rule.rule for rule in app.url_map.iter_rules()]
        print(f"✅ Found {len(routes)} routes:")
        for route in sorted(routes):
            print(f"   🔗 {route}")
            
    except Exception as e:
        print(f"❌ Dashboard failed: {e}")

def run_all_tests():
    """Run all debug tests"""
    print("🐿️ Nutflix Platform - Debug Test Suite")
    print("=" * 60)
    
    # Create logs directory
    os.makedirs('logs', exist_ok=True)
    
    # Run all tests
    test_imports()
    test_config()
    test_hardware_detection()
    test_camera_init()
    test_motion_detector()
    test_flask_dashboard()
    
    print("\n🎯 Debug Test Complete!")
    print("=" * 60)
    print("Check logs/debug_test.log for detailed output")
    print("\nNext steps:")
    print("1. Fix any ❌ errors shown above")
    print("2. Install missing dependencies")
    print("3. Check hardware connections")
    print("4. Run: python3 devices/nutpod/main.py")

if __name__ == "__main__":
    run_all_tests()
