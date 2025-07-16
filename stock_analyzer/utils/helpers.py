import os
import json
from stock_analyzer.utils.config import default_config

def get_config_path():
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')

def load_config():
    config_path = get_config_path()
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                merged_config = default_config.copy()
                merged_config.update(config)
                return merged_config
        except (json.JSONDecodeError, IOError):
            pass
    return default_config.copy()

def save_config(config):
    config_path = get_config_path()
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except IOError:
        return False
