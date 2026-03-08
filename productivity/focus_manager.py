from datetime import datetime
import threading

class FocusManager:
    def __init__(self, analytics_tracker=None):
        self.focus_active = False
        self.focus_start_time = None
        self.analytics_tracker = analytics_tracker
        self.focus_timer = None
        
        self.blocked_sites = ["youtube", "facebook", "twitter", "netflix", "instagram", "reddit"]
        self.blocked_apps = ["game", "steam", "discord"]

    def enable(self, duration_minutes=None):
        if self.focus_active:
            return "Focus mode is already active."
        self.focus_active = True
        self.focus_start_time = datetime.now()
        
        if duration_minutes:
            self.focus_timer = threading.Timer(duration_minutes * 60, self._auto_disable)
            self.focus_timer.start()
            return f"Focus mode enabled for {duration_minutes} minutes. Distractions blocked."
            
        return "Focus mode enabled. Distractions blocked."

    def disable(self):
        if not self.focus_active:
            return "Focus mode is not active."
            
        if self.focus_timer:
            self.focus_timer.cancel()
            self.focus_timer = None
            
        duration = (datetime.now() - self.focus_start_time).total_seconds() / 60
        if self.analytics_tracker:
            self.analytics_tracker.log_focus_minutes(duration)
            
        self.focus_active = False
        self.focus_start_time = None
        return "Focus mode disabled."

    def _auto_disable(self):
        duration = (datetime.now() - self.focus_start_time).total_seconds() / 60
        if self.analytics_tracker:
            self.analytics_tracker.log_focus_minutes(duration)
            
        self.focus_active = False
        self.focus_start_time = None
        print("\n[System] Focus session complete.")
        
    def is_active(self):
        return self.focus_active

    def is_blocked(self, command: str) -> bool:
        lower = command.lower()
        if any(site in lower for site in self.blocked_sites):
            return True
        if any(app in lower for app in self.blocked_apps):
            return True
        return False
