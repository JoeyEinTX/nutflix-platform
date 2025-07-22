"""
SettingsManager: Load, update, and save device settings from config.json.
Uses config_manager to determine file path.
"""

import json
import os
from typing import Any
from core.config.config_manager import get_config, ConfigError

class SettingsError(Exception):
    pass

class SettingsManager:
    def __init__(self, device_name: str):
        self.device_name = device_name
        self.config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'devices', device_name, 'config.json')
        try:
            self._settings = get_config(device_name).copy()
        except ConfigError as e:
            raise SettingsError(f"Failed to load config: {e}")

    def get_setting(self, key: str) -> Any:
        if key not in self._settings:
            raise SettingsError(f"Setting '{key}' not found in config.")
        return self._settings[key]

    def update_setting(self, key: str, value: Any):
        if key not in self._settings:
            raise SettingsError(f"Setting '{key}' not found in config.")
        self._settings[key] = value

    def save_settings(self) -> None:
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self._settings, f, indent=2)
        except Exception as e:
            raise SettingsError(f"Failed to save settings: {e}")
