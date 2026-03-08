import os
import json

class ConfigManager:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.config_dir = os.path.join(self.base_dir, "config")
        self.config_file = os.path.join(self.config_dir, "config.json")
        self.config = self._load_config()

    def _load_config(self):
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
        
        if not os.path.exists(self.config_file):
            default_config = {
                "auto_start": False,
                "daemon_mode": False,
                "log_max_size_kb": 512,
                "save_directory": "Desktop/Jarvis",
                "blocked_sites": ["youtube", "instagram", "facebook", "twitter", "reddit"],
                "blocked_apps": ["steam", "epic", "vlc", "spotify"],
                "app_aliases": {}
            }
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(default_config, f, indent=4)
            return default_config

        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                loaded.setdefault("app_aliases", {})
                return loaded
        except Exception:
            return {}

    def get(self, key, default=None):
        return self.config.get(key, default)
