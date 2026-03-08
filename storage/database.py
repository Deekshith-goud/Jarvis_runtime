import sqlite3
from datetime import datetime


class DatabaseManager:
    def __init__(self):
        self._conn = sqlite3.connect("jarvis.db", check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        cursor = self._conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT,
                status TEXT,
                created_at TEXT,
                completed_at TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message TEXT,
                remind_at TEXT,
                delivered INTEGER DEFAULT 0
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS work_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_time TEXT,
                end_time TEXT,
                duration_minutes REAL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analytics_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                command TEXT,
                category TEXT,
                success INTEGER,
                timestamp TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS macros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                actions TEXT
            )
        """)
        self._conn.commit()

    def add_task(self, text: str) -> bool:
        cursor = self._conn.cursor()
        cursor.execute("SELECT id FROM tasks WHERE task = ? AND status = 'pending'", (text,))
        if cursor.fetchone():
            return False
            
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO tasks (task, status, created_at, completed_at) VALUES (?, ?, ?, ?)",
            (text, "pending", now, None),
        )
        self._conn.commit()
        return True

    def list_tasks(self) -> list:
        cursor = self._conn.cursor()
        cursor.execute("SELECT id, task, status, created_at FROM tasks WHERE status = 'pending'")
        return [dict(row) for row in cursor.fetchall()]

    def mark_task_done(self, task_id: int):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor = self._conn.cursor()
        cursor.execute(
            "UPDATE tasks SET status = 'done', completed_at = ? WHERE id = ?",
            (now, task_id),
        )
        self._conn.commit()

    def delete_task(self, task_id: int):
        cursor = self._conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        self._conn.commit()

    def get_last_pending_task(self):
        cursor = self._conn.cursor()
        cursor.execute(
            "SELECT id, task, created_at FROM tasks WHERE status = 'pending' ORDER BY id DESC LIMIT 1"
        )
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

    def add_reminder(self, message: str, remind_at: str):
        cursor = self._conn.cursor()
        cursor.execute(
            "INSERT INTO reminders (message, remind_at, delivered) VALUES (?, ?, 0)",
            (message, remind_at),
        )
        self._conn.commit()

    def get_due_reminders(self, current_time: str) -> list:
        cursor = self._conn.cursor()
        cursor.execute(
            "SELECT id, message FROM reminders WHERE delivered = 0 AND remind_at <= ?",
            (current_time,),
        )
        return [dict(row) for row in cursor.fetchall()]

    def mark_reminder_delivered(self, reminder_id: int):
        cursor = self._conn.cursor()
        cursor.execute(
            "UPDATE reminders SET delivered = 1 WHERE id = ?",
            (reminder_id,),
        )
        self._conn.commit()

    def get_upcoming_reminders(self, current_time: str, limit_time: str) -> list:
        cursor = self._conn.cursor()
        cursor.execute(
            "SELECT id, message, remind_at FROM reminders WHERE delivered = 0 AND remind_at >= ? AND remind_at <= ?",
            (current_time, limit_time),
        )
        return [dict(row) for row in cursor.fetchall()]

    def add_work_session(self, start_time: str, end_time: str, duration_minutes: float):
        cursor = self._conn.cursor()
        cursor.execute(
            "INSERT INTO work_sessions (start_time, end_time, duration_minutes) VALUES (?, ?, ?)",
            (start_time, end_time, duration_minutes),
        )
        self._conn.commit()

    def get_today_work_minutes(self, date_prefix: str) -> float:
        cursor = self._conn.cursor()
        cursor.execute(
            "SELECT SUM(duration_minutes) FROM work_sessions WHERE start_time LIKE ?",
            (date_prefix + "%",)
        )
        result = cursor.fetchone()[0]
        return result if result else 0.0

    def add_analytics_log(self, command: str, category: str, success: bool, timestamp: str):
        cursor = self._conn.cursor()
        cursor.execute(
            "INSERT INTO analytics_logs (command, category, success, timestamp) VALUES (?, ?, ?, ?)",
            (command, category, 1 if success else 0, timestamp)
        )
        self._conn.commit()

    def get_command_count_by_date(self, date_prefix: str) -> int:
        cursor = self._conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM analytics_logs WHERE timestamp LIKE ?", (date_prefix + "%",))
        return cursor.fetchone()[0]

    def get_most_used_command(self) -> str:
        cursor = self._conn.cursor()
        cursor.execute("SELECT command, COUNT(*) as c FROM analytics_logs GROUP BY command ORDER BY c DESC LIMIT 1")
        row = cursor.fetchone()
        return row["command"] if row else None

    def get_ai_call_stats(self, date_prefix: str) -> tuple:
        cursor = self._conn.cursor()
        cursor.execute("SELECT COUNT(*), SUM(success) FROM analytics_logs WHERE category = 'ai_system' AND timestamp LIKE ?", (date_prefix + "%",))
        row = cursor.fetchone()
        total = row[0] if row[0] else 0
        success = row[1] if row[1] else 0
        return (total, success, total - success)

    def get_task_completion_count(self, date_prefix: str) -> int:
        cursor = self._conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'done' AND completed_at LIKE ?", (date_prefix + "%",))
        return cursor.fetchone()[0]

    def get_delivered_reminder_count(self, date_prefix: str) -> int:
        cursor = self._conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM reminders WHERE delivered = 1 AND remind_at LIKE ?", (date_prefix + "%",))
        return cursor.fetchone()[0]

    def create_macro(self, name: str, actions: str) -> bool:
        cursor = self._conn.cursor()
        try:
            cursor.execute("INSERT OR REPLACE INTO macros (name, actions) VALUES (?, ?)", (name, actions))
            self._conn.commit()
            return True
        except sqlite3.Error:
            return False

    def delete_macro(self, name: str) -> bool:
        cursor = self._conn.cursor()
        cursor.execute("DELETE FROM macros WHERE name = ?", (name,))
        self._conn.commit()
        return cursor.rowcount > 0

    def list_macros(self) -> list:
        cursor = self._conn.cursor()
        cursor.execute("SELECT name, actions FROM macros ORDER BY name")
        return [dict(row) for row in cursor.fetchall()]

    def get_macro(self, name: str) -> str | None:
        cursor = self._conn.cursor()
        cursor.execute("SELECT actions FROM macros WHERE name = ?", (name,))
        row = cursor.fetchone()
        return row["actions"] if row else None
