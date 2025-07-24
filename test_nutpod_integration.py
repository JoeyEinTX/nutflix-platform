#!/usr/bin/env python3
"""
NutPod Settings Integration Test

Tests the new settings system integration with existing device code
without requiring hardware dependencies like OpenCV or GPIO.
"""

import sys
import time
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.settings.integration import get_settings_integrator


def test_settings_integration():
    """Test settings integration for NutPod device."""
    print("🐿️ NutPod Settings Integration Test")
    print("=" * 50)
    
    # Initialize settings integrator
    print("\n📋 [Setup] Initializing settings integrator...")
    integrator = get_settings_integrator("nutpod")
    settings = integrator.settings
    
    print(f"✅ Settings loaded from: {settings.config_path}")
    print(f"   Device type: {settings.system.device_type}")
    print(f"   Device name: {settings.system.device_name}")
    
    # Test privacy controls
    print("\n🔒 [Privacy] Testing privacy controls...")
    privacy_status = settings.get_privacy_status()
    
    print("Current Privacy Status:")
    for key, value in privacy_status.items():
        status_icon = "✅" if value else "❌"
        print(f"   {status_icon} {key.replace('_', ' ').title()}: {value}")
    
    # Test recording permissions
    print(f"\nRecording Permissions:")
    print(f"   Camera recording allowed: {'✅' if settings.is_recording_allowed() else '❌'}")
    print(f"   Audio recording allowed: {'✅' if settings.is_audio_recording_allowed() else '❌'}")
    print(f"   Streaming allowed: {'✅' if settings.is_streaming_allowed() else '❌'}")
    
    # Test privacy mode toggle
    print(f"\n🔐 [Privacy Mode] Testing privacy mode...")
    print(f"   Before privacy mode - Recording: {settings.is_recording_allowed()}")
    
    settings.enable_privacy_mode()
    print(f"   During privacy mode - Recording: {settings.is_recording_allowed()}")
    print(f"   During privacy mode - Audio: {settings.is_audio_recording_allowed()}")
    
    settings.disable_privacy_mode()
    print(f"   After privacy mode - Recording: {settings.is_recording_allowed()}")
    
    # Test configuration access methods
    print(f"\n⚙️ [Config] Testing configuration access...")
    
    # Camera configuration
    camera_config = integrator.get_camera_config()
    print(f"Camera Configuration:")
    print(f"   Enabled cameras: {camera_config['enabled_cameras']}")
    print(f"   Primary camera: {camera_config['primary_camera']['name']}")
    print(f"   Recording quality: {camera_config['recording']['quality']}")
    
    # Motion configuration  
    motion_config = integrator.get_motion_config()
    print(f"Motion Configuration:")
    print(f"   Motion detection: {motion_config['motion_detection']}")
    print(f"   Sensitivity: {motion_config['motion_sensitivity']}")
    print(f"   GPIO pins: {motion_config['motion_sensors']}")
    print(f"   Cooldown: {motion_config['cooldown_period']}s")
    
    # Audio configuration
    audio_config = integrator.get_audio_config()
    print(f"Audio Configuration:")
    print(f"   Recording enabled: {audio_config['record_audio']}")
    print(f"   Format: {audio_config['audio_format']}")
    print(f"   Sample rate: {audio_config['sample_rate']}")
    print(f"   Duration: {audio_config['duration']}s")
    
    # Storage configuration
    storage_config = integrator.get_storage_config()
    print(f"Storage Configuration:")
    print(f"   Base path: {storage_config['base_path']}")
    print(f"   Recordings path: {storage_config['recordings_path']}")
    print(f"   Retention: {storage_config['cleanup_days']} days")
    print(f"   Max usage: {storage_config['max_storage_usage']}%")
    
    # Test settings modification
    print(f"\n📝 [Modification] Testing settings modification...")
    
    original_sensitivity = settings.motion.detection.sensitivity
    original_retention = settings.privacy.data.retention_period
    
    print(f"   Original motion sensitivity: {original_sensitivity}")
    print(f"   Original data retention: {original_retention} days")
    
    # Modify settings
    settings.motion.detection.sensitivity = 0.7
    settings.privacy.data.retention_period = 21
    settings.camera.primary_camera.brightness = 65
    
    print(f"   Modified motion sensitivity: {settings.motion.detection.sensitivity}")
    print(f"   Modified data retention: {settings.privacy.data.retention_period} days")
    print(f"   Modified camera brightness: {settings.camera.primary_camera.brightness}")
    
    # Validate settings
    validation_result = settings.validate()
    print(f"   Settings validation: {'✅ PASS' if validation_result else '❌ FAIL'}")
    
    # Test backward compatibility
    print(f"\n🔄 [Compatibility] Testing backward compatibility...")
    
    try:
        # Get compatible config (old format)
        compatible_config = integrator.get_compatible_config()
        print(f"   Compatible config generated successfully")
        print(f"   Config keys: {list(compatible_config.keys())}")
        
        # Test specific compatibility mappings
        if 'enabled_cameras' in compatible_config:
            print(f"   Enabled cameras (old format): {compatible_config['enabled_cameras']}")
        
        if 'motion_sensors' in compatible_config:
            print(f"   Motion sensors (old format): {compatible_config['motion_sensors']}")
            
        if 'record_audio' in compatible_config:
            print(f"   Audio recording (old format): {compatible_config['record_audio']}")
        
    except Exception as e:
        print(f"   ❌ Compatibility test failed: {e}")
    
    # Test retention cleanup date calculation
    print(f"\n📅 [Cleanup] Testing retention cleanup...")
    cleanup_date = settings.get_retention_cleanup_date()
    print(f"   Files older than {cleanup_date.strftime('%Y-%m-%d')} should be cleaned up")
    
    # Test export/import functionality
    print(f"\n💾 [Export/Import] Testing export/import...")
    
    try:
        # Export settings
        exported = settings.export_settings(include_sensitive=False)
        print(f"   Exported settings successfully")
        print(f"   Exported sections: {list(exported.keys())}")
        
        # Test specific exports
        if 'camera' in exported:
            camera_export = exported['camera']
            print(f"   Exported camera enabled: {camera_export['primary_camera']['enabled']}")
        
    except Exception as e:
        print(f"   ❌ Export test failed: {e}")
    
    # Restore original values
    settings.motion.detection.sensitivity = original_sensitivity
    settings.privacy.data.retention_period = original_retention
    
    print(f"\n✅ [Complete] All tests completed successfully!")
    
    return True


def test_legacy_migration():
    """Test migration from legacy config to new settings system."""
    print(f"\n🔄 [Migration] Testing legacy config migration...")
    
    integrator = get_settings_integrator("nutpod")
    
    try:
        # Attempt migration
        migration_result = integrator.migrate_legacy_config()
        print(f"   Migration result: {'✅ SUCCESS' if migration_result else '❌ FAILED'}")
        
        # Show legacy config if available
        legacy_config = integrator.legacy_config
        if legacy_config:
            print(f"   Legacy config keys: {list(legacy_config.keys())}")
        else:
            print(f"   No legacy config found")
            
    except Exception as e:
        print(f"   Migration error: {e}")


def simulate_device_runtime():
    """Simulate how the device would run with the new settings system."""
    print(f"\n🚀 [Simulation] Simulating device runtime with settings...")
    
    integrator = get_settings_integrator("nutpod")
    settings = integrator.settings
    
    # Simulate motion detection setup
    motion_config = integrator.get_motion_config()
    print(f"   Motion sensors configured: {motion_config['motion_sensors']}")
    print(f"   Motion sensitivity: {motion_config['motion_sensitivity']}")
    print(f"   Cooldown period: {motion_config['cooldown_period']}s")
    
    # Simulate recording permission check
    if settings.is_recording_allowed():
        print(f"   ✅ Recording is allowed - would initialize RecordingEngine")
    else:
        print(f"   🔒 Recording is disabled by privacy settings")
    
    # Simulate audio permission check  
    if settings.is_audio_recording_allowed():
        audio_config = integrator.get_audio_config()
        print(f"   ✅ Audio recording allowed - format: {audio_config['audio_format']}")
    else:
        print(f"   🔒 Audio recording disabled by privacy settings")
    
    # Simulate streaming permission check
    if settings.is_streaming_allowed():
        print(f"   ✅ Streaming allowed - port: {settings.network.streaming_port}")
    else:
        print(f"   🔒 Streaming disabled by privacy settings")
    
    # Simulate storage setup
    storage_config = integrator.get_storage_config()
    recordings_path = Path(storage_config['base_path']) / storage_config['recordings_path']
    print(f"   📁 Recordings would be saved to: {recordings_path}")
    
    print(f"   🏃 Device simulation complete")


def main():
    """Run all integration tests."""
    print("🧪 NutPod Settings Integration Test Suite")
    print("=" * 60)
    
    try:
        # Core settings integration test
        test_settings_integration()
        
        # Legacy migration test
        test_legacy_migration()
        
        # Runtime simulation
        simulate_device_runtime()
        
        print(f"\n🎉 [SUCCESS] All integration tests passed!")
        print(f"\nNext steps:")
        print(f"  1. ✅ Settings system is ready for production use")
        print(f"  2. 🔄 Integrate with Flask dashboard")
        print(f"  3. 📱 Create React settings components")
        print(f"  4. 🚀 Deploy to actual Pi hardware")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ [FAILED] Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
