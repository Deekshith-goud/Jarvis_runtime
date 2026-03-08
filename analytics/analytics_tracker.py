from datetime import datetime

class AnalyticsTracker:
    def __init__(self, db_manager):
        self.db = db_manager

    def log_command(self, command: str, category: str, success: bool):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.db.add_analytics_log(command, category, success, now)

    def log_ai_call(self, success: bool):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.db.add_analytics_log("ai_call", "ai_system", success, now)

    def get_today_command_count(self):
        today = datetime.now().strftime("%Y-%m-%d")
        return self.db.get_command_count_by_date(today)

    def get_most_used_command(self):
        return self.db.get_most_used_command()

    def get_ai_stats(self):
        today = datetime.now().strftime("%Y-%m-%d")
        return self.db.get_ai_call_stats(today)

    def get_task_completion_count(self):
        today = datetime.now().strftime("%Y-%m-%d")
        return self.db.get_task_completion_count(today)

    def get_reminder_trigger_count(self):
        today = datetime.now().strftime("%Y-%m-%d")
        return self.db.get_delivered_reminder_count(today)

    def get_work_session_stats(self):
        today = datetime.now().strftime("%Y-%m-%d")
        return self.db.get_today_work_minutes(today)

    def log_focus_minutes(self, minutes: float):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.db.add_analytics_log(f"focus_{minutes:.1f}m", "focus_session", True, now)

    def get_focus_minutes_today(self) -> float:
        today = datetime.now().strftime("%Y-%m-%d")
        cursor = self.db._conn.cursor()
        cursor.execute("SELECT command FROM analytics_logs WHERE category = 'focus_session' AND timestamp LIKE ?", (today + "%",))
        total = 0.0
        for row in cursor.fetchall():
            try:
                # Extracts the '1.5' from 'focus_1.5m'
                val = row[0].replace("focus_", "").replace("m", "")
                total += float(val)
            except ValueError:
                pass
        return total
