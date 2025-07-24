"""
Settings Integration Helper

Bridges the existing config system with the new comprehensive settings system.
Provides backward compatibility while enabling migration to the new system.

This module helps integrate the new settings system with existing code that
uses the old config_manager.py system.
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path

from .settings_manager import SettingsManager, get_settings
from ..config.config_manager import get_config, ConfigError

logger = logging.getLogger(__name__)


class SettingsIntegrator:
    """
    Integrates old config system with new settings system.
    
    Provides compatibility layer and migration utilities.
    """
    
    def __init__(self, device_name: str):
        """
        Initialize settings integrator for a specific device.
        
        Args:
            device_name: Name of the device (nutpod, scoutpod, etc.)
        """
        self.device_name = device_name
        self._settings = None
        self._legacy_config = None
        
    @property
    def settings(self) -> SettingsManager:
        """Get the settings manager instance."""
        if self._settings is None:
            # Map device names to settings device types
            device_type_map = {
                'nutpod': 'nutpod',
                'scoutpod': 'scoutpod', 
                'groundpod': 'groundpod'
            }
            device_type = device_type_map.get(self.device_name, 'nutflix_lite')
            self._settings = SettingsManager(device_type=device_type)
        return self._settings
    
    @property
    def legacy_config(self) -> Dict[str, Any]:
        """Get legacy config for backward compatibility."""
        if self._legacy_config is None:
            try:
                self._legacy_config = get_config(self.device_name)
            except ConfigError as e:
                logger.warning(f"Could not load legacy config: {e}")
                self._legacy_config = {}
        return self._legacy_config
    
    def get_camera_config(self) -> Dict[str, Any]:
        """
        Get camera configuration with new settings system.
        
        Returns camera config in format expected by existing code.
        """
        settings = self.settings
        
        # Build camera config from new settings
        camera_config = {
            'enabled_cameras': [],
            'primary_camera': {
                'name': settings.camera.primary_camera.name,
                'enabled': settings.camera.primary_camera.enabled,
                'resolution': settings.camera.primary_camera.resolution,
                'framerate': settings.camera.primary_camera.framerate,
                'brightness': settings.camera.primary_camera.brightness,
                'contrast': settings.camera.primary_camera.contrast,
                'saturation': settings.camera.primary_camera.saturation
            },
            'secondary_camera': {
                'name': settings.camera.secondary_camera.name,
                'enabled': settings.camera.secondary_camera.enabled,
                'resolution': settings.camera.secondary_camera.resolution,
                'framerate': settings.camera.secondary_camera.framerate,
                'brightness': settings.camera.secondary_camera.brightness,
                'contrast': settings.camera.secondary_camera.contrast,
                'saturation': settings.camera.secondary_camera.saturation
            },
            'recording': {
                'quality': settings.camera.recording.quality,
                'format': settings.camera.recording.format,
                'max_duration': settings.camera.recording.max_clip_duration,
                'pre_buffer': settings.camera.recording.pre_record_buffer,
                'post_buffer': settings.camera.recording.post_record_buffer
            }
        }
        
        # Build enabled cameras list
        if settings.camera.primary_camera.enabled:
            camera_config['enabled_cameras'].append(settings.camera.primary_camera.name)
        if settings.camera.secondary_camera.enabled:
            camera_config['enabled_cameras'].append(settings.camera.secondary_camera.name)
            
        # Fall back to legacy config if needed
        if not camera_config['enabled_cameras'] and 'enabled_cameras' in self.legacy_config:
            camera_config['enabled_cameras'] = self.legacy_config['enabled_cameras']
            
        return camera_config
    
    def get_motion_config(self) -> Dict[str, Any]:
        """Get motion detection configuration."""
        settings = self.settings
        
        motion_config = {
            'motion_detection': settings.motion.detection.enabled,
            'motion_sensitivity': settings.motion.detection.sensitivity,
            'motion_sensors': dict(settings.motion.sensors.gpio_pins),
            'min_area': settings.motion.detection.min_area,
            'cooldown_period': settings.motion.detection.cooldown_period,
            'debounce_time': settings.motion.sensors.debounce_time
        }
        
        # Fall back to legacy config
        legacy = self.legacy_config
        if 'motion_sensors' in legacy and not motion_config['motion_sensors']:
            motion_config['motion_sensors'] = legacy['motion_sensors']
            
        return motion_config
    
    def get_audio_config(self) -> Dict[str, Any]:
        """Get audio configuration."""
        settings = self.settings
        
        audio_config = {
            'record_audio': settings.audio.recording.enabled,
            'audio_format': settings.audio.recording.format,
            'sample_rate': settings.audio.recording.sample_rate,
            'channels': settings.audio.recording.channels,
            'duration': settings.audio.recording.duration,
            'quality': settings.audio.recording.quality,
            'motion_triggered': settings.audio.triggers.motion_triggered,
            'noise_reduction': settings.audio.processing.noise_reduction,
            'auto_gain': settings.audio.processing.auto_gain,
            'volume_level': settings.audio.processing.volume_level
        }
        
        # Fall back to legacy config
        legacy = self.legacy_config
        if 'record_audio' in legacy:
            audio_config['record_audio'] = legacy['record_audio']
            
        return audio_config
    
    def get_storage_config(self) -> Dict[str, Any]:
        """Get storage configuration."""
        settings = self.settings
        
        storage_config = {
            'base_path': settings.storage.base_path,
            'recordings_path': settings.storage.recordings_path,
            'logs_path': settings.storage.logs_path,
            'cleanup_days': settings.privacy.data.retention_period,
            'max_storage_usage': settings.storage.max_storage_usage,
            'auto_cleanup': settings.storage.archive_old_files,  # Use archive_old_files as auto_cleanup
            'naming_pattern': settings.storage.naming_pattern
        }
        
        # Fall back to legacy config
        legacy = self.legacy_config
        if 'cleanup_days' in legacy:
            storage_config['cleanup_days'] = legacy['cleanup_days']
            
        return storage_config
    
    def get_ai_config(self) -> Dict[str, Any]:
        """Get AI configuration."""
        settings = self.settings
        
        ai_config = {
            'ai_model': settings.ai.model_path,
            'ai_enabled': settings.ai.detection_enabled,
            'confidence_threshold': settings.ai.confidence_threshold,
            'real_time': settings.ai.real_time_processing,
            'batch_processing': settings.ai.batch_processing
        }
        
        # Fall back to legacy config
        legacy = self.legacy_config
        if 'ai_model' in legacy:
            ai_config['ai_model'] = legacy['ai_model']
            
        return ai_config
    
    def get_privacy_status(self) -> Dict[str, Any]:
        """Get comprehensive privacy status."""
        return self.settings.get_privacy_status()
    
    def is_recording_allowed(self) -> bool:
        """Check if recording is allowed based on privacy settings."""
        return self.settings.is_recording_allowed()
    
    def is_audio_recording_allowed(self) -> bool:
        """Check if audio recording is allowed."""
        return self.settings.is_audio_recording_allowed()
    
    def is_streaming_allowed(self) -> bool:
        """Check if streaming is allowed."""
        return self.settings.is_streaming_allowed()
    
    def migrate_legacy_config(self) -> bool:
        """
        Migrate settings from legacy config.json to new settings system.
        
        Returns:
            True if migration was successful, False otherwise
        """
        try:
            legacy = self.legacy_config
            if not legacy:
                logger.info("No legacy config to migrate")
                return True
                
            settings = self.settings
            
            # Migrate camera settings
            if 'enabled_cameras' in legacy:
                cameras = legacy['enabled_cameras']
                if cameras:
                    settings.camera.primary_camera.name = cameras[0] if len(cameras) > 0 else "CritterCam"
                    settings.camera.primary_camera.enabled = len(cameras) > 0
                    if len(cameras) > 1:
                        settings.camera.secondary_camera.name = cameras[1]
                        settings.camera.secondary_camera.enabled = True
            
            # Migrate motion settings
            if 'motion_sensitivity' in legacy:
                settings.motion.detection.sensitivity = legacy['motion_sensitivity']
            if 'motion_sensors' in legacy:
                settings.motion.sensors.gpio_pins = legacy['motion_sensors']
                
            # Migrate audio settings
            if 'record_audio' in legacy:
                settings.audio.recording.enabled = legacy['record_audio']
                
            # Migrate storage settings
            if 'cleanup_days' in legacy:
                settings.privacy.data.retention_period = legacy['cleanup_days']
                
            # Migrate AI settings
            if 'ai_model' in legacy:
                settings.ai.model_path = legacy['ai_model']
                
            # Save migrated settings
            settings.save()
            
            logger.info(f"Successfully migrated legacy config for {self.device_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to migrate legacy config: {e}")
            return False
    
    def get_compatible_config(self) -> Dict[str, Any]:
        """
        Get a complete config dict that's compatible with existing code.
        
        This combines new settings with legacy config format for backward compatibility.
        """
        config = {}
        
        # Get all configuration sections
        config.update(self.get_camera_config())
        config.update(self.get_motion_config())
        config.update(self.get_audio_config())
        config.update(self.get_storage_config())
        config.update(self.get_ai_config())
        
        # Add device info
        config['device_name'] = self.device_name
        config['device_type'] = self.settings.system.device_type
        
        # Add privacy controls
        config['privacy_status'] = self.get_privacy_status()
        
        return config


# Global integrator instances for each device type
_integrators: Dict[str, SettingsIntegrator] = {}

def get_settings_integrator(device_name: str) -> SettingsIntegrator:
    """Get settings integrator instance for a device."""
    if device_name not in _integrators:
        _integrators[device_name] = SettingsIntegrator(device_name)
    return _integrators[device_name]


def get_integrated_config(device_name: str) -> Dict[str, Any]:
    """
    Get integrated configuration that combines new settings with legacy compatibility.
    
    This is a drop-in replacement for the old get_config() function that provides
    both new settings functionality and backward compatibility.
    """
    integrator = get_settings_integrator(device_name)
    return integrator.get_compatible_config()
