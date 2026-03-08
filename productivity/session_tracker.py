from datetime import datetime

class SessionTracker:
    def __init__(self, db_manager):
        self.db = db_manager
        self.current_start = None

    def start_session(self):
        if self.current_start is not None:
            return "Session already in progress."
        self.current_start = datetime.now()
        return "Work session started."

    def end_session(self):
        if self.current_start is None:
            return "No active work session to end."
        now = datetime.now()
        duration = (now - self.current_start).total_seconds() / 60.0
        start_str = self.current_start.strftime("%Y-%m-%d %H:%M:%S")
        end_str = now.strftime("%Y-%m-%d %H:%M:%S")
        self.db.add_work_session(start_str, end_str, duration)
        self.current_start = None
        return f"Work session ended. Duration: {duration:.1f} minutes."

    def get_current_duration(self):
        if self.current_start is None:
            return 0.0
        return (datetime.now() - self.current_start).total_seconds() / 60.0

    def get_today_total_minutes(self):
        today_prefix = datetime.now().strftime("%Y-%m-%d")
        total = self.db.get_today_work_minutes(today_prefix)
        total += self.get_current_duration()
        return total
