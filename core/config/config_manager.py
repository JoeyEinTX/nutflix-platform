
"""
ConfigManager: Loads and caches device config from /devices/{device_name}/config.json
Future-ready for .env override support.
"""

import json
import os
from typing import Dict

_config_cache: Dict[str, dict] = {}

class ConfigError(Exception):
    pass

def get_config(device_name: str) -> dict:
    """
    Loads and caches config for the given device_name.
    Raises ConfigError if file is missing or malformed.
    """
    if device_name in _config_cache:
        return _config_cache[device_name]
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                               'devices', device_name, 'config.json')
    if not os.path.isfile(config_path):
        raise ConfigError(f"Config file not found: {config_path}\nDid you create devices/{device_name}/config.json?")
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        raise ConfigError(f"Malformed config file: {config_path}\n{e}")
    _config_cache[device_name] = config
    return config

# Future: add .env override support here
