"""
Helper functions for the application.
"""

import os
import json
from stock_analyzer.utils.config import default_config

def format_currency(value):
    """
    Format a number as a currency string.
    """
    # TODO: Implement currency formatting
    return str(value)

def get_config_path():
    """
    Get the path to the config file.
    """
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')

def load_config():
    """
    Load configuration from file or return defaults.
    """
    config_path = get_config_path()
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                # Merge with defaults to ensure all keys exist
                merged_config = default_config.copy()
                merged_config.update(config)
                return merged_config
        except (json.JSONDecodeError, IOError):
            pass
    return default_config.copy()

def save_config(config):
    """
    Save configuration to file.
    """
    config_path = get_config_path()
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except IOError:
        return False 