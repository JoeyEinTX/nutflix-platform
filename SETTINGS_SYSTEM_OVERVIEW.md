# 🐿️ Nutflix Lite Settings & Privacy System

**Version:** 1.0  
**Created:** July 24, 2025  
**Status:** ✅ Ready for Integration

## 🎯 Overview

A comprehensive, modular settings and privacy management system for Nutflix wildlife monitoring devices. Designed for forward compatibility and easy Flask dashboard integration.

## 🏗️ Architecture

### **Core Components:**
- **`settings_manager.py`**: Type-safe settings management with persistent storage
- **`default_settings.yaml`**: Comprehensive schema and defaults  
- **`integration.py`**: Backward compatibility bridge for existing code
- **`demo_settings.py`**: Complete demonstration and testing script

### **Design Principles:**
- **Type-Safe Access**: Dataclass-based properties with validation
- **Logical Grouping**: Settings organized by function (camera, privacy, etc.)
- **Persistent Storage**: YAML-based with atomic saves and backups
- **Privacy-First**: Comprehensive privacy controls built-in
- **Forward Compatible**: Ready for cloud storage and multi-device scaling

## 📋 Settings Groups

### **Camera Settings**
```python
settings.camera.primary_camera.enabled = True
settings.camera.primary_camera.resolution = "1920x1080"
settings.camera.recording.quality = "high"
```

### **Motion Detection**
```python
settings.motion.detection.sensitivity = 0.6
settings.motion.detection.cooldown_period = 10
settings.motion.sensors.gpio_pins = {"CritterCam": 17}
```

### **Audio Configuration**
```python
settings.audio.recording.enabled = True
settings.audio.recording.sample_rate = 44100
settings.audio.triggers.motion_triggered = True
```

### **Privacy Controls** 🔒
```python
# Check permissions
if settings.is_recording_allowed():
    start_recording()

# Privacy mode
settings.enable_privacy_mode()  # Disables all recording/streaming
settings.disable_privacy_mode()

# Privacy status
status = settings.get_privacy_status()
```

### **Power Management**
```python
settings.power.mode = "eco"  # performance, balanced, eco
settings.power.cpu_max_usage = 70
settings.power.sleep_enabled = True
```

### **Network Configuration**
```python
settings.network.streaming_enabled = True
settings.network.streaming_port = 5000
settings.network.hostname = "nutflix-device-01"
```

### **Storage Management**
```python
settings.storage.base_path = "/home/pi/nutflix-data"
settings.storage.max_storage_usage = 80
settings.privacy.data.retention_period = 30  # days
```

## 🔒 Privacy System Features

### **Recording Controls**
- Camera recording enable/disable
- Audio recording toggle
- Streaming permissions
- Privacy mode (disables everything)

### **Data Management**
- Configurable retention periods
- Auto-cleanup based on age/space
- Local-only storage enforcement
- Field of view warnings

### **Logging & Monitoring**
- System log controls
- Access log retention
- Debug log enable/disable
- Privacy notifications

## 🚀 Usage Examples

### **Basic Usage**
```python
from core.settings.settings_manager import SettingsManager

# Initialize for device type
settings = SettingsManager(device_type="nutpod")

# Type-safe access
if settings.camera.primary_camera.enabled:
    resolution = settings.camera.primary_camera.resolution
    
# Modify and save
settings.motion.detection.sensitivity = 0.7
settings.save()
```

### **Privacy Controls**
```python
# Check if recording is allowed
if settings.is_recording_allowed():
    recorder.start()

# Enable privacy mode
settings.enable_privacy_mode()

# Get comprehensive privacy status
privacy = settings.get_privacy_status()
print(f"Recording allowed: {privacy['camera_recording']}")
```

### **Legacy Integration**
```python
from core.settings.integration import get_integrated_config

# Drop-in replacement for old get_config()
config = get_integrated_config("nutpod")
cameras = config['enabled_cameras']  # Works with existing code
```

## 🔧 Flask Dashboard Integration

### **Settings API Endpoints**
```python
from core.settings.settings_manager import get_settings

@app.route('/api/settings', methods=['GET'])
def get_all_settings():
    settings = get_settings()
    return jsonify(settings.export_settings())

@app.route('/api/settings/privacy', methods=['GET'])
def get_privacy_status():
    settings = get_settings()
    return jsonify(settings.get_privacy_status())

@app.route('/api/settings/privacy/mode', methods=['POST'])
def toggle_privacy_mode():
    settings = get_settings()
    if request.json.get('enabled'):
        settings.enable_privacy_mode()
    else:
        settings.disable_privacy_mode()
    settings.save()
    return jsonify({'success': True})
```

### **React Component Integration**
```javascript
// Privacy Controls Component
const PrivacyControls = () => {
  const [privacyStatus, setPrivacyStatus] = useState({});
  
  useEffect(() => {
    fetch('/api/settings/privacy')
      .then(r => r.json())
      .then(setPrivacyStatus);
  }, []);
  
  const togglePrivacyMode = async () => {
    await fetch('/api/settings/privacy/mode', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({enabled: !privacyStatus.privacy_mode})
    });
    // Refresh status
  };
  
  return (
    <div>
      <h3>Privacy Controls</h3>
      <label>
        <input 
          type="checkbox" 
          checked={privacyStatus.privacy_mode || false}
          onChange={togglePrivacyMode}
        />
        Privacy Mode (Disable All Recording)
      </label>
      <p>Camera Recording: {privacyStatus.camera_recording ? '✅' : '❌'}</p>
      <p>Audio Recording: {privacyStatus.audio_recording ? '✅' : '❌'}</p>
    </div>
  );
};
```

## 📦 Device-Specific Configurations

### **NutPod (Full Featured)**
- Dual cameras enabled
- Audio recording enabled
- Streaming enabled
- Full AI processing
- Extended storage retention

### **ScoutPod (Portable)**
- Single camera only
- Audio disabled (battery saving)
- No streaming
- Minimal storage retention
- Power-optimized settings

### **GroundPod (Specialized)**
- Thermal camera support
- Ground-level specific settings
- Minimal retention
- Specialized AI models

## 🔄 Migration & Compatibility

### **Legacy Config Migration**
```python
from core.settings.integration import get_settings_integrator

integrator = get_settings_integrator("nutpod")
success = integrator.migrate_legacy_config()
```

### **Backward Compatibility**
```python
# Old code continues to work
from core.settings.integration import get_integrated_config
config = get_integrated_config("nutpod")
cameras = config['enabled_cameras']  # Still works
```

## 🚀 Future Extensions

### **Cloud Storage Integration**
```yaml
storage:
  cloud:
    enabled: false
    provider: "aws_s3"  # aws_s3, google_cloud, azure
    bucket: "nutflix-recordings"
    sync_schedule: "daily"
    local_backup: true
```

### **Multi-Device Management**
```yaml
network:
  device_discovery: true
  mesh_networking: false
  central_management: false
```

### **Advanced AI Features**
```yaml
ai:
  models:
    - name: "wildlife_detection"
      enabled: true
      confidence: 0.7
    - name: "species_classification" 
      enabled: false
      confidence: 0.8
```

## ✅ Testing & Validation

### **Run Demo**
```bash
cd /workspaces/nutflix-platform
python3 demo_settings.py
```

### **Integration Test**
```bash
# Test with existing nutpod code
python3 devices/nutpod/main.py
```

### **Settings Validation**
```python
settings = SettingsManager()
is_valid = settings.validate()  # Returns True/False
```

## 📋 Next Steps

1. **✅ COMPLETE**: Core settings system implemented
2. **🔄 IN PROGRESS**: Flask dashboard integration
3. **📋 TODO**: React component library
4. **📋 TODO**: Device-specific configuration overrides
5. **📋 TODO**: Cloud storage preferences
6. **📋 TODO**: Real-time settings sync
7. **📋 TODO**: Settings backup/restore system

## 🎉 Benefits Achieved

- **✅ Type-Safe**: No more string-based config access
- **✅ Privacy-First**: Comprehensive privacy controls built-in  
- **✅ Future-Ready**: Extensible for cloud and multi-device
- **✅ Backward Compatible**: Existing code continues to work
- **✅ UI-Ready**: Designed for easy dashboard integration
- **✅ Persistent**: Automatic saving with backup protection
- **✅ Validated**: Schema validation and error handling
- **✅ Modular**: Logical grouping for maintainability

This settings system provides a solid foundation for your Nutflix platform that will scale from Nutflix Lite to the full multi-device ecosystem! 🐿️
