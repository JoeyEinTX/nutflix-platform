# 🔧 Settings System Update - Integration Guide

**Generated:** July 24, 2025  
**Purpose:** Documentation for sub-repo team to integrate new settings system

## 📋 Overview

We've rebuilt the settings and privacy system for Nutflix Platform with a comprehensive, type-safe, privacy-first architecture. This document outlines what's changed and what the GUI sub-repo needs to know for integration.

## 🆕 What's New

### **New Settings Architecture:**
- **YAML-based configuration** with JSON fallback
- **Type-safe dataclass properties** for all settings groups
- **Comprehensive privacy controls** with recording toggles
- **Persistent storage** with atomic saves and backups
- **Legacy compatibility bridge** for existing code
- **Thread-safe operations** for concurrent access

### **Key Files Added:**
```
core/settings/
├── settings_manager.py      # Main settings manager class
├── default_settings.yaml    # Complete schema & defaults  
├── integration.py          # Legacy compatibility bridge
└── __init__.py
```

## 🎯 Settings Groups Structure

The new system organizes settings into logical groups:

### **1. Camera Settings**
```python
settings.camera.primary_camera.enabled
settings.camera.primary_camera.name
settings.camera.primary_camera.resolution  
settings.camera.primary_camera.brightness
settings.camera.recording.quality
settings.camera.recording.fps
```

### **2. Privacy Settings** 🔒
```python
settings.privacy.recording.camera_recording_enabled
settings.privacy.recording.audio_recording_enabled  
settings.privacy.recording.streaming_enabled
settings.privacy.mode.privacy_mode_enabled
settings.privacy.data.retention_period
settings.privacy.data.local_storage_only
```

### **3. Motion Detection**
```python
settings.motion.detection.enabled
settings.motion.detection.sensitivity
settings.motion.detection.min_area
settings.motion.sensors.gpio_pins
settings.motion.timing.cooldown_period
```

### **4. Audio Settings**
```python
settings.audio.recording.enabled
settings.audio.recording.format
settings.audio.recording.sample_rate
settings.audio.recording.duration
```

### **5. Storage Settings**
```python
settings.storage.base_path
settings.storage.recordings_path
settings.storage.max_storage_usage
settings.storage.archive_old_files
```

### **6. Network & Power**
```python
settings.network.streaming_port
settings.network.api_port
settings.power.low_power_mode
settings.power.sleep_schedule
```

## 🔒 Privacy System Features

### **Privacy Mode Toggle:**
```python
# Enable privacy mode (disables all recording/streaming)
settings.enable_privacy_mode()

# Disable privacy mode (restores previous settings)  
settings.disable_privacy_mode()

# Check privacy status
privacy_status = settings.get_privacy_status()
```

### **Recording Permissions:**
```python
# Check if recording is allowed
can_record = settings.is_recording_allowed()
can_record_audio = settings.is_audio_recording_allowed()
can_stream = settings.is_streaming_allowed()
```

### **Data Retention:**
```python
# Get cleanup date based on retention period
cleanup_date = settings.get_retention_cleanup_date()

# Privacy status includes retention info
privacy_status['data_retention_days']
```

## 🔧 Integration Methods

### **For GUI Settings Menu:**

#### **1. Get Current Settings:**
```python
from core.settings.integration import get_settings_integrator

# Initialize for specific device type
integrator = get_settings_integrator("nutpod")
settings = integrator.settings

# Get all settings for display
current_config = {
    "camera_enabled": settings.camera.primary_camera.enabled,
    "recording_quality": settings.camera.recording.quality,
    "motion_sensitivity": settings.motion.detection.sensitivity,
    "privacy_mode": settings.privacy.mode.privacy_mode_enabled,
    "audio_recording": settings.privacy.recording.audio_recording_enabled,
    "retention_days": settings.privacy.data.retention_period,
    # ... add all settings your GUI needs
}
```

#### **2. Update Settings:**
```python
# Update individual settings
settings.camera.primary_camera.brightness = new_brightness
settings.motion.detection.sensitivity = new_sensitivity
settings.privacy.data.retention_period = new_retention

# Validate changes
if settings.validate():
    # Save to persistent storage
    settings.save()
    success = True
else:
    success = False
```

#### **3. Privacy Controls for GUI:**
```python
# Privacy toggle button
def toggle_privacy_mode():
    if settings.privacy.mode.privacy_mode_enabled:
        settings.disable_privacy_mode()
    else:
        settings.enable_privacy_mode()
    settings.save()

# Recording permission toggles
def toggle_camera_recording():
    settings.privacy.recording.camera_recording_enabled = not settings.privacy.recording.camera_recording_enabled
    settings.save()

def toggle_audio_recording():
    settings.privacy.recording.audio_recording_enabled = not settings.privacy.recording.audio_recording_enabled  
    settings.save()
```

#### **4. Export/Import for GUI:**
```python
# Export settings for backup/sharing
exported = settings.export_settings(include_sensitive=False)

# Import settings from backup
success = settings.import_settings(imported_data)
```

## 📱 Recommended GUI Components

Based on the new settings structure, your GUI should include:

### **Privacy Section** 🔒
- **Privacy Mode Toggle** (master switch)
- **Camera Recording Toggle**
- **Audio Recording Toggle** 
- **Streaming Toggle**
- **Data Retention Slider** (7-90 days)
- **Local Storage Only Checkbox**

### **Camera Section** 📷
- **Camera Enable/Disable**
- **Resolution Dropdown**
- **Quality Slider** (low/medium/high/ultra)
- **Brightness/Contrast Sliders**
- **FPS Setting**

### **Motion Detection Section** 🔍
- **Motion Detection Toggle**
- **Sensitivity Slider** (0.1-1.0)
- **Minimum Area Slider**
- **Cooldown Period** (seconds)

### **Audio Section** 🎵
- **Audio Recording Toggle**
- **Format Dropdown** (wav/mp3/flac)
- **Quality Setting**
- **Duration Slider**

### **Storage Section** 💾
- **Base Storage Path**
- **Max Storage Usage** (percentage)
- **Auto Cleanup Toggle**
- **Storage Usage Display**

### **System Section** ⚙️
- **Device Name**
- **Low Power Mode**
- **Sleep Schedule**
- **Network Ports**

## 🔄 Backward Compatibility

### **For Existing Code:**
The new system includes a compatibility bridge, so existing code should continue working:

```python
# Old way (still works)
from core.config.config_manager import ConfigManager
config = ConfigManager().get_config()

# New way (recommended)
from core.settings.integration import get_settings_integrator
integrator = get_settings_integrator("nutpod")
settings = integrator.settings
```

### **Migration Support:**
```python
# Automatic migration from old config
integrator.migrate_legacy_config()

# Get config in old format for compatibility
old_format_config = integrator.get_compatible_config()
```

## 🚀 Next Steps for Sub-Repo Team

1. **Review this document** and identify which settings your GUI currently manages
2. **Test compatibility** with existing GUI using the compatibility bridge
3. **Plan GUI updates** to support new privacy controls and settings groups
4. **Coordinate timing** for when to switch from legacy to new system
5. **Test integration** using the provided integration methods

## ⚠️ Important Notes

- **Privacy-first design**: All recording features can be disabled
- **Type safety**: Settings are validated before saving
- **Thread safety**: Multiple components can access settings safely
- **Atomic saves**: Settings changes are saved atomically with backups
- **Device-specific**: Each device type can have different defaults

## 📞 Questions for Sub-Repo Team

1. Which settings does your current GUI manage?
2. Do you need additional privacy controls we haven't covered?
3. What's your preferred timeline for integration?
4. Do you need any additional export/import features?
5. Any specific validation requirements for settings?

Let's coordinate to ensure smooth integration! 🤝
