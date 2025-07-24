"""
Nutflix Lite Settings Manager

A comprehensive settings management system for Nutflix wildlife monitoring devices.
Provides type-safe access to configuration with persistent storage, defaults, and
privacy controls.

Features:
- YAML-based configuration with JSON fallback
- Type-safe property access
- Logical grouping (camera, motion, audio, privacy, etc.)
- Persistent storage with atomic writes
- Schema validation and defaults
- Privacy system integration
- Future-ready for cloud storage and multi-device management

Usage:
    from core.settings.settings_manager import SettingsManager
    
    settings = SettingsManager()
    
    # Type-safe access
    if settings.camera.primary.enabled:
        resolution = settings.camera.primary.resolution
        
    # Privacy controls
    if settings.privacy.camera.recording_enabled:
        start_recording()
        
    # Modify and save
    settings.motion.detection.sensitivity = 0.6
    settings.save()
"""

import os
import yaml
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import threading
from copy import deepcopy

logger = logging.getLogger(__name__)


class SettingsError(Exception):
    """Base exception for settings-related errors."""
    pass


class SettingsValidationError(SettingsError):
    """Raised when settings validation fails."""
    pass


@dataclass
class CameraSettings:
    """Camera configuration settings."""
    enabled: bool = True
    name: str = ""
    resolution: str = "1920x1080"
    framerate: int = 30
    brightness: int = 50
    contrast: int = 50
    saturation: int = 50


@dataclass
class RecordingSettings:
    """Recording configuration settings."""
    quality: str = "high"
    format: str = "mp4"
    max_clip_duration: int = 30
    pre_record_buffer: float = 2.0
    post_record_buffer: float = 3.0


@dataclass
class CameraGroup:
    """Camera settings group."""
    primary_camera: CameraSettings = field(default_factory=CameraSettings)
    secondary_camera: CameraSettings = field(default_factory=CameraSettings)
    recording: RecordingSettings = field(default_factory=RecordingSettings)


@dataclass
class MotionDetectionSettings:
    """Motion detection configuration."""
    enabled: bool = True
    sensitivity: float = 0.4
    min_area: int = 500
    cooldown_period: int = 10
    zones: list = field(default_factory=list)


@dataclass
class MotionSensors:
    """Motion sensor configuration."""
    gpio_pins: Dict[str, int] = field(default_factory=dict)
    debounce_time: float = 2.0


@dataclass
class MotionGroup:
    """Motion detection settings group."""
    detection: MotionDetectionSettings = field(default_factory=MotionDetectionSettings)
    sensors: MotionSensors = field(default_factory=MotionSensors)


@dataclass
class AudioRecordingSettings:
    """Audio recording configuration."""
    enabled: bool = True
    format: str = "wav"
    sample_rate: int = 44100
    channels: int = 1
    duration: int = 10
    quality: str = "medium"


@dataclass
class AudioTriggersSettings:
    """Audio trigger configuration."""
    motion_triggered: bool = True
    continuous: bool = False
    scheduled: bool = False


@dataclass
class AudioProcessingSettings:
    """Audio processing configuration."""
    noise_reduction: bool = True
    auto_gain: bool = True
    volume_level: int = 75


@dataclass
class AudioGroup:
    """Audio settings group."""
    recording: AudioRecordingSettings = field(default_factory=AudioRecordingSettings)
    triggers: AudioTriggersSettings = field(default_factory=AudioTriggersSettings)
    processing: AudioProcessingSettings = field(default_factory=AudioProcessingSettings)


@dataclass
class CameraPrivacySettings:
    """Camera privacy controls."""
    recording_enabled: bool = True
    streaming_enabled: bool = True
    privacy_mode: bool = False
    field_of_view_warning: bool = True


@dataclass
class AudioPrivacySettings:
    """Audio privacy controls."""
    recording_enabled: bool = True
    privacy_mode: bool = False


@dataclass
class DataPrivacySettings:
    """Data retention and storage privacy."""
    retention_period: int = 30
    auto_cleanup: bool = True
    local_storage_only: bool = True


@dataclass
class LoggingPrivacySettings:
    """Logging privacy controls."""
    system_logs: bool = True
    access_logs: bool = True
    debug_logs: bool = False
    log_retention: int = 7


@dataclass
class NotificationPrivacySettings:
    """Privacy notification settings."""
    recording_indicator: bool = True
    privacy_mode_alerts: bool = True
    data_retention_warnings: bool = True


@dataclass
class PrivacyGroup:
    """Privacy settings group."""
    camera: CameraPrivacySettings = field(default_factory=CameraPrivacySettings)
    audio: AudioPrivacySettings = field(default_factory=AudioPrivacySettings)
    data: DataPrivacySettings = field(default_factory=DataPrivacySettings)
    logging: LoggingPrivacySettings = field(default_factory=LoggingPrivacySettings)
    notifications: NotificationPrivacySettings = field(default_factory=NotificationPrivacySettings)


@dataclass
class PowerSettings:
    """Power management settings."""
    mode: str = "balanced"
    sleep_enabled: bool = False
    sleep_start_time: str = "22:00"
    sleep_end_time: str = "06:00"
    cpu_max_usage: int = 80
    throttle_temperature: int = 70
    camera_idle_timeout: int = 300
    camera_quick_wake: bool = True


@dataclass
class NetworkSettings:
    """Network configuration settings."""
    hostname: str = "nutflix-lite"
    wifi_auto_connect: bool = True
    wifi_power_save: bool = False
    streaming_enabled: bool = True
    streaming_port: int = 5000
    streaming_quality: str = "medium"
    streaming_max_viewers: int = 3
    ssh_enabled: bool = True
    web_interface: bool = True
    api_enabled: bool = True


@dataclass
class StorageSettings:
    """Storage configuration settings."""
    base_path: str = "/home/pi/nutflix-data"
    recordings_path: str = "recordings"
    logs_path: str = "logs"
    temp_path: str = "temp"
    max_storage_usage: int = 80
    cleanup_threshold: int = 90
    archive_old_files: bool = True
    date_folders: bool = True
    camera_subfolders: bool = True
    naming_pattern: str = "%Y%m%d_%H%M%S"


@dataclass
class AISettings:
    """AI and detection settings."""
    detection_enabled: bool = False
    model_path: str = "models/wildlife_detection.tflite"
    confidence_threshold: float = 0.7
    real_time_processing: bool = False
    batch_processing: bool = True


@dataclass
class SystemSettings:
    """System configuration settings."""
    device_type: str = "nutflix_lite"
    device_name: str = "Nutflix Lite Device"
    device_location: str = ""
    timezone: str = "UTC"
    ntp_enabled: bool = True
    auto_update: bool = False
    update_check_interval: int = 24
    monitoring_enabled: bool = True
    cpu_alerts: bool = True
    memory_alerts: bool = True
    temperature_alerts: bool = True


class SettingsManager:
    """
    Comprehensive settings management for Nutflix devices.
    
    Provides type-safe access to configuration settings with persistent storage,
    validation, and privacy controls.
    """
    
    def __init__(self, config_path: Optional[str] = None, device_type: str = "nutflix_lite"):
        """
        Initialize the settings manager.
        
        Args:
            config_path: Path to settings file (defaults to user config directory)
            device_type: Type of device (nutflix_lite, nutpod, scoutpod, etc.)
        """
        self.device_type = device_type
        self._lock = threading.Lock()
        
        # Determine config file path
        if config_path:
            self.config_path = Path(config_path)
        else:
            config_dir = Path.home() / ".config" / "nutflix"
            config_dir.mkdir(parents=True, exist_ok=True)
            self.config_path = config_dir / f"{device_type}_settings.yaml"
            
        # Load default settings
        self._load_defaults()
        
        # Load user settings (if they exist)
        self._load_user_settings()
        
        # Initialize type-safe property groups
        self._init_property_groups()
        
        logger.info(f"Settings manager initialized for {device_type}")
        logger.info(f"Config path: {self.config_path}")
    
    def _load_defaults(self):
        """Load default settings from the bundled YAML file."""
        try:
            # Find the default settings file
            current_dir = Path(__file__).parent
            defaults_path = current_dir / "default_settings.yaml"
            
            if not defaults_path.exists():
                raise SettingsError(f"Default settings file not found: {defaults_path}")
                
            with open(defaults_path, 'r') as f:
                self._defaults = yaml.safe_load(f)
                
            # Start with defaults as current settings
            self._settings = deepcopy(self._defaults)
            
            logger.debug("Default settings loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load default settings: {e}")
            raise SettingsError(f"Could not load default settings: {e}")
    
    def _load_user_settings(self):
        """Load user-specific settings from persistent storage."""
        if not self.config_path.exists():
            logger.info("No user settings file found, using defaults")
            return
            
        try:
            with open(self.config_path, 'r') as f:
                if self.config_path.suffix.lower() == '.json':
                    user_settings = json.load(f)
                else:
                    user_settings = yaml.safe_load(f)
                    
            # Merge user settings with defaults (user settings take precedence)
            self._merge_settings(self._settings, user_settings)
            
            logger.info(f"User settings loaded from {self.config_path}")
            
        except Exception as e:
            logger.error(f"Failed to load user settings: {e}")
            # Continue with defaults on error
    
    def _merge_settings(self, defaults: dict, user_settings: dict):
        """Recursively merge user settings into defaults."""
        for key, value in user_settings.items():
            if key in defaults and isinstance(defaults[key], dict) and isinstance(value, dict):
                self._merge_settings(defaults[key], value)
            else:
                defaults[key] = value
    
    def _init_property_groups(self):
        """Initialize type-safe property groups from loaded settings."""
        try:
            # Camera settings
            cam_data = self._settings.get('camera', {})
            self.camera = CameraGroup(
                primary_camera=CameraSettings(**cam_data.get('primary_camera', {})),
                secondary_camera=CameraSettings(**cam_data.get('secondary_camera', {})),
                recording=RecordingSettings(**cam_data.get('recording', {}))
            )
            
            # Motion settings
            motion_data = self._settings.get('motion', {})
            self.motion = MotionGroup(
                detection=MotionDetectionSettings(**motion_data.get('detection', {})),
                sensors=MotionSensors(**motion_data.get('sensors', {}))
            )
            
            # Audio settings
            audio_data = self._settings.get('audio', {})
            self.audio = AudioGroup(
                recording=AudioRecordingSettings(**audio_data.get('recording', {})),
                triggers=AudioTriggersSettings(**audio_data.get('triggers', {})),
                processing=AudioProcessingSettings(**audio_data.get('processing', {}))
            )
            
            # Privacy settings
            privacy_data = self._settings.get('privacy', {})
            self.privacy = PrivacyGroup(
                camera=CameraPrivacySettings(**privacy_data.get('camera', {})),
                audio=AudioPrivacySettings(**privacy_data.get('audio', {})),
                data=DataPrivacySettings(**privacy_data.get('data', {})),
                logging=LoggingPrivacySettings(**privacy_data.get('logging', {})),
                notifications=NotificationPrivacySettings(**privacy_data.get('notifications', {}))
            )
            
            # Power settings - handle nested structure
            power_data = self._settings.get('power', {})
            sleep_data = power_data.get('sleep', {})
            cpu_data = power_data.get('cpu', {})
            camera_data = power_data.get('camera', {})
            
            self.power = PowerSettings(
                mode=power_data.get('mode', 'balanced'),
                sleep_enabled=sleep_data.get('enabled', False),
                sleep_start_time=sleep_data.get('start_time', '22:00'),
                sleep_end_time=sleep_data.get('end_time', '06:00'),
                cpu_max_usage=cpu_data.get('max_usage', 80),
                throttle_temperature=cpu_data.get('throttle_temperature', 70),
                camera_idle_timeout=camera_data.get('idle_timeout', 300),
                camera_quick_wake=camera_data.get('quick_wake', True)
            )
            
            # Network settings - handle nested structure
            network_data = self._settings.get('network', {})
            wifi_data = network_data.get('wifi', {})
            streaming_data = network_data.get('streaming', {})
            remote_data = network_data.get('remote', {})
            
            self.network = NetworkSettings(
                hostname=network_data.get('hostname', 'nutflix-lite'),
                wifi_auto_connect=wifi_data.get('auto_connect', True),
                wifi_power_save=wifi_data.get('power_save', False),
                streaming_enabled=streaming_data.get('enabled', True),
                streaming_port=streaming_data.get('port', 5000),
                streaming_quality=streaming_data.get('quality', 'medium'),
                streaming_max_viewers=streaming_data.get('max_viewers', 3),
                ssh_enabled=remote_data.get('ssh_enabled', True),
                web_interface=remote_data.get('web_interface', True),
                api_enabled=remote_data.get('api_enabled', True)
            )
            
            # Storage settings - handle nested structure  
            storage_data = self._settings.get('storage', {})
            local_data = storage_data.get('local', {})
            management_data = storage_data.get('management', {})
            organization_data = storage_data.get('organization', {})
            
            self.storage = StorageSettings(
                base_path=local_data.get('base_path', '/home/pi/nutflix-data'),
                recordings_path=local_data.get('recordings_path', 'recordings'),
                logs_path=local_data.get('logs_path', 'logs'),
                temp_path=local_data.get('temp_path', 'temp'),
                max_storage_usage=management_data.get('max_storage_usage', 80),
                cleanup_threshold=management_data.get('cleanup_threshold', 90),
                archive_old_files=management_data.get('archive_old_files', True),
                date_folders=organization_data.get('date_folders', True),
                camera_subfolders=organization_data.get('camera_subfolders', True),
                naming_pattern=organization_data.get('naming_pattern', '%Y%m%d_%H%M%S')
            )
            
            # AI settings - handle nested structure
            ai_data = self._settings.get('ai', {})
            detection_data = ai_data.get('detection', {})
            processing_data = ai_data.get('processing', {})
            
            self.ai = AISettings(
                detection_enabled=detection_data.get('enabled', False),
                model_path=detection_data.get('model_path', 'models/wildlife_detection.tflite'),
                confidence_threshold=detection_data.get('confidence_threshold', 0.7),
                real_time_processing=processing_data.get('real_time', False),
                batch_processing=processing_data.get('batch_processing', True)
            )
            
            # System settings - handle nested structure
            system_data = self._settings.get('system', {})
            device_data = system_data.get('device', {})
            time_data = system_data.get('time', {})
            updates_data = system_data.get('updates', {})
            monitoring_data = system_data.get('monitoring', {})
            
            self.system = SystemSettings(
                device_type=device_data.get('type', 'nutflix_lite'),
                device_name=device_data.get('name', 'Nutflix Lite Device'),
                device_location=device_data.get('location', ''),
                timezone=time_data.get('timezone', 'UTC'),
                ntp_enabled=time_data.get('ntp_enabled', True),
                auto_update=updates_data.get('auto_update', False),
                update_check_interval=updates_data.get('check_interval', 24),
                monitoring_enabled=monitoring_data.get('enabled', True),
                cpu_alerts=monitoring_data.get('cpu_alerts', True),
                memory_alerts=monitoring_data.get('memory_alerts', True),
                temperature_alerts=monitoring_data.get('temperature_alerts', True)
            )
            
        except Exception as e:
            logger.error(f"Failed to initialize property groups: {e}")
            raise SettingsError(f"Settings initialization failed: {e}")
    
    def save(self):
        """Save current settings to persistent storage."""
        with self._lock:
            try:
                # Convert property groups back to dict format
                settings_dict = self._serialize_settings()
                
                # Create backup of existing file
                if self.config_path.exists():
                    backup_path = self.config_path.with_suffix(f'.backup_{int(datetime.now().timestamp())}')
                    self.config_path.rename(backup_path)
                
                # Write new settings atomically
                temp_path = self.config_path.with_suffix('.tmp')
                with open(temp_path, 'w') as f:
                    yaml.dump(settings_dict, f, default_flow_style=False, indent=2)
                    
                temp_path.rename(self.config_path)
                
                logger.info(f"Settings saved to {self.config_path}")
                
            except Exception as e:
                logger.error(f"Failed to save settings: {e}")
                raise SettingsError(f"Could not save settings: {e}")
    
    def _serialize_settings(self) -> dict:
        """Convert property groups back to dictionary format for saving."""
        from dataclasses import asdict
        
        return {
            'camera': {
                'primary_camera': asdict(self.camera.primary_camera),
                'secondary_camera': asdict(self.camera.secondary_camera),
                'recording': asdict(self.camera.recording)
            },
            'motion': {
                'detection': asdict(self.motion.detection),
                'sensors': asdict(self.motion.sensors)
            },
            'audio': {
                'recording': asdict(self.audio.recording),
                'triggers': asdict(self.audio.triggers),
                'processing': asdict(self.audio.processing)
            },
            'privacy': {
                'camera': asdict(self.privacy.camera),
                'audio': asdict(self.privacy.audio),
                'data': asdict(self.privacy.data),
                'logging': asdict(self.privacy.logging),
                'notifications': asdict(self.privacy.notifications)
            },
            'power': {
                'mode': self.power.mode,
                'sleep': {
                    'enabled': self.power.sleep_enabled,
                    'start_time': self.power.sleep_start_time,
                    'end_time': self.power.sleep_end_time
                },
                'cpu': {
                    'max_usage': self.power.cpu_max_usage,
                    'throttle_temperature': self.power.throttle_temperature
                },
                'camera': {
                    'idle_timeout': self.power.camera_idle_timeout,
                    'quick_wake': self.power.camera_quick_wake
                }
            },
            'network': {
                'hostname': self.network.hostname,
                'wifi': {
                    'auto_connect': self.network.wifi_auto_connect,
                    'power_save': self.network.wifi_power_save
                },
                'streaming': {
                    'enabled': self.network.streaming_enabled,
                    'port': self.network.streaming_port,
                    'quality': self.network.streaming_quality,
                    'max_viewers': self.network.streaming_max_viewers
                },
                'remote': {
                    'ssh_enabled': self.network.ssh_enabled,
                    'web_interface': self.network.web_interface,
                    'api_enabled': self.network.api_enabled
                }
            },
            'storage': {
                'local': {
                    'base_path': self.storage.base_path,
                    'recordings_path': self.storage.recordings_path,
                    'logs_path': self.storage.logs_path,
                    'temp_path': self.storage.temp_path
                },
                'management': {
                    'max_storage_usage': self.storage.max_storage_usage,
                    'cleanup_threshold': self.storage.cleanup_threshold,
                    'archive_old_files': self.storage.archive_old_files
                },
                'organization': {
                    'date_folders': self.storage.date_folders,
                    'camera_subfolders': self.storage.camera_subfolders,
                    'naming_pattern': self.storage.naming_pattern
                }
            },
            'ai': {
                'detection': {
                    'enabled': self.ai.detection_enabled,
                    'model_path': self.ai.model_path,
                    'confidence_threshold': self.ai.confidence_threshold
                },
                'processing': {
                    'real_time': self.ai.real_time_processing,
                    'batch_processing': self.ai.batch_processing
                }
            },
            'system': {
                'device': {
                    'type': self.system.device_type,
                    'name': self.system.device_name,
                    'location': self.system.device_location
                },
                'time': {
                    'timezone': self.system.timezone,
                    'ntp_enabled': self.system.ntp_enabled
                },
                'updates': {
                    'auto_update': self.system.auto_update,
                    'check_interval': self.system.update_check_interval
                },
                'monitoring': {
                    'enabled': self.system.monitoring_enabled,
                    'cpu_alerts': self.system.cpu_alerts,
                    'memory_alerts': self.system.memory_alerts,
                    'temperature_alerts': self.system.temperature_alerts
                }
            }
        }
    
    def reset_to_defaults(self):
        """Reset all settings to defaults."""
        with self._lock:
            self._settings = deepcopy(self._defaults)
            self._init_property_groups()
            logger.info("Settings reset to defaults")
    
    def validate(self) -> bool:
        """Validate current settings."""
        try:
            # Basic validation rules
            errors = []
            
            # Camera validation
            if self.camera.primary_camera.framerate < 1 or self.camera.primary_camera.framerate > 60:
                errors.append("Primary camera framerate must be between 1-60 fps")
                
            # Motion validation
            if not 0.0 <= self.motion.detection.sensitivity <= 1.0:
                errors.append("Motion sensitivity must be between 0.0 and 1.0")
                
            # Privacy validation
            if self.privacy.data.retention_period < 1:
                errors.append("Data retention period must be at least 1 day")
                
            # Storage validation
            if not 10 <= self.storage.max_storage_usage <= 95:
                errors.append("Max storage usage must be between 10-95%")
                
            if errors:
                logger.error(f"Settings validation failed: {errors}")
                raise SettingsValidationError("; ".join(errors))
                
            return True
            
        except Exception as e:
            logger.error(f"Settings validation error: {e}")
            return False
    
    def get_privacy_status(self) -> Dict[str, Any]:
        """Get comprehensive privacy status."""
        return {
            'camera_recording': self.privacy.camera.recording_enabled and not self.privacy.camera.privacy_mode,
            'camera_streaming': self.privacy.camera.streaming_enabled and not self.privacy.camera.privacy_mode,
            'audio_recording': self.privacy.audio.recording_enabled and not self.privacy.audio.privacy_mode,
            'privacy_mode': self.privacy.camera.privacy_mode or self.privacy.audio.privacy_mode,
            'data_retention_days': self.privacy.data.retention_period,
            'local_storage_only': self.privacy.data.local_storage_only,
            'field_of_view_warning': self.privacy.camera.field_of_view_warning
        }
    
    def enable_privacy_mode(self):
        """Enable full privacy mode (disables all recording and streaming)."""
        with self._lock:
            self.privacy.camera.privacy_mode = True
            self.privacy.audio.privacy_mode = True
            logger.info("Privacy mode enabled")
    
    def disable_privacy_mode(self):
        """Disable privacy mode (restores normal operation)."""
        with self._lock:
            self.privacy.camera.privacy_mode = False
            self.privacy.audio.privacy_mode = False
            logger.info("Privacy mode disabled")
    
    def is_recording_allowed(self) -> bool:
        """Check if recording is currently allowed based on privacy settings."""
        return (self.privacy.camera.recording_enabled and 
                not self.privacy.camera.privacy_mode and
                self.camera.primary_camera.enabled)
    
    def is_audio_recording_allowed(self) -> bool:
        """Check if audio recording is currently allowed."""
        return (self.privacy.audio.recording_enabled and 
                not self.privacy.audio.privacy_mode and
                self.audio.recording.enabled)
    
    def is_streaming_allowed(self) -> bool:
        """Check if streaming is currently allowed."""
        return (self.privacy.camera.streaming_enabled and 
                not self.privacy.camera.privacy_mode and
                self.network.streaming_enabled)
    
    def get_retention_cleanup_date(self) -> datetime:
        """Get the date before which files should be cleaned up."""
        return datetime.now() - timedelta(days=self.privacy.data.retention_period)
    
    def export_settings(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """Export settings for backup or transfer."""
        settings = self._serialize_settings()
        
        if not include_sensitive:
            # Remove sensitive information
            if 'network' in settings:
                settings['network'].pop('ssh_enabled', None)
            if 'system' in settings:
                settings['system'].pop('device_location', None)
                
        return settings
    
    def import_settings(self, settings_dict: Dict[str, Any], validate: bool = True):
        """Import settings from dictionary."""
        with self._lock:
            # Backup current settings
            old_settings = self._serialize_settings()
            
            try:
                # Merge imported settings
                self._merge_settings(self._settings, settings_dict)
                self._init_property_groups()
                
                if validate and not self.validate():
                    raise SettingsValidationError("Imported settings failed validation")
                
                logger.info("Settings imported successfully")
                
            except Exception as e:
                # Restore old settings on error
                self._settings = old_settings
                self._init_property_groups()
                logger.error(f"Settings import failed: {e}")
                raise


# Convenience function for global settings access
_global_settings: Optional[SettingsManager] = None

def get_settings(device_type: str = "nutflix_lite") -> SettingsManager:
    """Get global settings manager instance."""
    global _global_settings
    if _global_settings is None:
        _global_settings = SettingsManager(device_type=device_type)
    return _global_settings
