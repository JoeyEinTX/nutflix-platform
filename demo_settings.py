#!/usr/bin/env python3
"""
Nutflix Lite Settings System Demo

This script demonstrates the new settings and privacy system.
Run this to test the settings manager and see how it works.
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.settings.settings_manager import SettingsManager, get_settings


def demo_basic_usage():
    """Demonstrate basic settings usage."""
    print("🐿️ Nutflix Lite Settings System Demo")
    print("=" * 50)
    
    # Initialize settings manager
    settings = SettingsManager()
    
    print("\n📹 Camera Settings:")
    print(f"  Primary camera enabled: {settings.camera.primary_camera.enabled}")
    print(f"  Primary camera name: {settings.camera.primary_camera.name}")
    print(f"  Resolution: {settings.camera.primary_camera.resolution}")
    print(f"  Recording quality: {settings.camera.recording.quality}")
    
    print("\n🎯 Motion Detection:")
    print(f"  Enabled: {settings.motion.detection.enabled}")
    print(f"  Sensitivity: {settings.motion.detection.sensitivity}")
    print(f"  Cooldown: {settings.motion.detection.cooldown_period}s")
    
    print("\n🎵 Audio Settings:")
    print(f"  Recording enabled: {settings.audio.recording.enabled}")
    print(f"  Format: {settings.audio.recording.format}")
    print(f"  Sample rate: {settings.audio.recording.sample_rate}")
    print(f"  Motion triggered: {settings.audio.triggers.motion_triggered}")
    
    return settings


def demo_privacy_controls(settings):
    """Demonstrate privacy controls."""
    print("\n🔒 Privacy Controls:")
    print("=" * 30)
    
    # Show current privacy status
    privacy_status = settings.get_privacy_status()
    print("\nCurrent Privacy Status:")
    for key, value in privacy_status.items():
        print(f"  {key.replace('_', ' ').title()}: {value}")
    
    # Check recording permissions
    print(f"\nRecording allowed: {settings.is_recording_allowed()}")
    print(f"Audio recording allowed: {settings.is_audio_recording_allowed()}")
    print(f"Streaming allowed: {settings.is_streaming_allowed()}")
    
    # Demonstrate privacy mode
    print("\n🔐 Enabling Privacy Mode...")
    settings.enable_privacy_mode()
    
    print(f"Recording allowed after privacy mode: {settings.is_recording_allowed()}")
    print(f"Audio recording allowed after privacy mode: {settings.is_audio_recording_allowed()}")
    
    # Restore normal operation
    print("\n🔓 Disabling Privacy Mode...")
    settings.disable_privacy_mode()
    
    print(f"Recording allowed after disabling privacy mode: {settings.is_recording_allowed()}")


def demo_settings_modification(settings):
    """Demonstrate modifying and saving settings."""
    print("\n⚙️ Settings Modification:")
    print("=" * 30)
    
    # Show original values
    print(f"\nOriginal motion sensitivity: {settings.motion.detection.sensitivity}")
    print(f"Original data retention: {settings.privacy.data.retention_period} days")
    
    # Modify settings
    settings.motion.detection.sensitivity = 0.6
    settings.privacy.data.retention_period = 14
    settings.camera.primary_camera.brightness = 60
    
    print(f"\nModified motion sensitivity: {settings.motion.detection.sensitivity}")
    print(f"Modified data retention: {settings.privacy.data.retention_period} days")
    print(f"Modified camera brightness: {settings.camera.primary_camera.brightness}")
    
    # Validate settings
    print(f"\nSettings validation: {'✅ PASS' if settings.validate() else '❌ FAIL'}")
    
    # Save settings (commented out to avoid creating files in demo)
    print("\n💾 Settings would be saved to:", settings.config_path)
    # settings.save()


def demo_storage_and_power(settings):
    """Demonstrate storage and power management settings."""
    print("\n💾 Storage & Power Settings:")
    print("=" * 35)
    
    print(f"\nStorage base path: {settings.storage.base_path}")
    print(f"Max storage usage: {settings.storage.max_storage_usage}%")
    print(f"Archive old files: {settings.storage.archive_old_files}")
    print(f"Date folders: {settings.storage.date_folders}")
    
    print(f"\nPower mode: {settings.power.mode}")
    print(f"CPU max usage: {settings.power.cpu_max_usage}%")
    print(f"Camera idle timeout: {settings.power.camera_idle_timeout}s")
    
    print(f"\nRetention cleanup date: {settings.get_retention_cleanup_date().strftime('%Y-%m-%d')}")


def demo_network_settings(settings):
    """Demonstrate network settings."""
    print("\n🌐 Network Settings:")
    print("=" * 25)
    
    print(f"\nHostname: {settings.network.hostname}")
    print(f"Streaming enabled: {settings.network.streaming_enabled}")
    print(f"Streaming port: {settings.network.streaming_port}")
    print(f"Max viewers: {settings.network.streaming_max_viewers}")
    print(f"Web interface: {settings.network.web_interface}")
    print(f"API enabled: {settings.network.api_enabled}")


def demo_device_types():
    """Demonstrate different device type configurations."""
    print("\n🤖 Different Device Types:")
    print("=" * 30)
    
    device_types = ["nutflix_lite", "nutpod", "scoutpod", "groundpod"]
    
    for device_type in device_types:
        print(f"\n{device_type.upper()}:")
        # Note: This would load device-specific settings in a real implementation
        temp_settings = SettingsManager(device_type=device_type)
        print(f"  Device type: {temp_settings.system.device_type}")
        print(f"  Device name: {temp_settings.system.device_name}")
        print(f"  Primary camera: {temp_settings.camera.primary_camera.name}")


def demo_export_import(settings):
    """Demonstrate settings export/import."""
    print("\n📤 Export/Import Demo:")
    print("=" * 25)
    
    # Export settings
    exported = settings.export_settings(include_sensitive=False)
    print(f"\nExported settings keys: {list(exported.keys())}")
    
    # Show camera settings from export
    if 'camera' in exported:
        cam_settings = exported['camera']
        print(f"Exported camera primary enabled: {cam_settings['primary_camera']['enabled']}")
        print(f"Exported recording quality: {cam_settings['recording']['quality']}")


def main():
    """Run the complete demo."""
    try:
        # Basic usage demo
        settings = demo_basic_usage()
        
        # Privacy controls demo
        demo_privacy_controls(settings)
        
        # Settings modification demo
        demo_settings_modification(settings)
        
        # Storage and power demo
        demo_storage_and_power(settings)
        
        # Network settings demo
        demo_network_settings(settings)
        
        # Device types demo
        demo_device_types()
        
        # Export/import demo
        demo_export_import(settings)
        
        print("\n✅ Demo completed successfully!")
        print("\nNext steps:")
        print("  1. Integrate with your Flask dashboard")
        print("  2. Add device-specific configuration overrides")
        print("  3. Implement cloud storage preferences")
        print("  4. Add real-time settings change notifications")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
