import os
import json
from config.settings import CONFIG_FILE
from core.entity_resolver import resolve_entity

class EntityRegistry:
    def __init__(self):
        self.websites = {
            "youtube": "https://youtube.com",
            "google": "https://google.com",
            "chatgpt": "https://chatgpt.com",
            "gemini": "https://gemini.google.com",
            "notebooklm": "https://notebooklm.google.com"
        }
        
        self.applications = {
            "notepad": "notepad",
            "chrome": "chrome",
            "cursor": "cursor"
        }
        
        self.aliases = {
            "yt": "youtube",
            "gpt": "chatgpt",
            "goog": "google",
            "youtub": "youtube",
            "chat gpt": "chatgpt"
        }
        
        self._load_config_extensions()
        
    def _load_config_extensions(self):
        if not os.path.exists(CONFIG_FILE):
            return
            
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
                
            custom_websites = config.get("custom_websites", {})
            for k, v in custom_websites.items():
                self.websites[k.lower()] = v
                
            custom_apps = config.get("custom_apps", {})
            for k, v in custom_apps.items():
                self.applications[k.lower()] = v
                
            custom_aliases = config.get("custom_aliases", {})
            for k, v in custom_aliases.items():
                self.aliases[k.lower()] = v.lower()
        except Exception:
            pass
            
    def resolve(self, name: str) -> tuple[str, str] | None:
        name_lower = name.lower().strip()
        
        # 1. Check alias exact match
        if name_lower in self.aliases:
            canonical = self.aliases[name_lower]
        else:
            canonical = name_lower
            
        # 2. Check canonical exact match
        if canonical in self.websites:
            return ("website", self.websites[canonical])
        if canonical in self.applications:
            return ("application", self.applications[canonical])
            
        # 3. Fuzzy match against canonical keys (cutoff=0.75)
        all_canonical = list(self.websites.keys()) + list(self.applications.keys())
        entity, conf = resolve_entity(canonical, all_canonical)
        
        if conf >= 0.75 and entity:
            if entity in self.websites:
                return ("website", self.websites[entity])
            if entity in self.applications:
                return ("application", self.applications[entity])
                
        return None
