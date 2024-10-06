# backend/config_manager.py

import os
import json
import logging
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class ConfigManager:
    def __init__(self, config_path=None):
        if not config_path:
            config_path = resource_path(os.path.join('config', 'config.json'))
        self.config_path = config_path
        if not os.path.exists(os.path.dirname(self.config_path)):
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        if not os.path.isfile(self.config_path):
            self.create_default_config()

    def create_default_config(self):
        default_config = {
            "aws_access_key": "",
            "aws_secret_key": "",
            "region": "us-east-2",
            "sync_folder": "",
            "bucket_name": "",
            "aws_profile": ""
        }
        with open(self.config_path, 'w') as f:
            json.dump(default_config, f, indent=4)
        logger.info("Default configuration file created.")

    def load_config(self):
        with open(self.config_path, 'r') as f:
            config = json.load(f)
        logger.info("Configuration loaded.")
        return config

    def save_config(self, config):
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=4)
        logger.info("Configuration saved.")
