import threading
import time
from datetime import datetime


class ReminderScheduler(threading.Thread):
    def __init__(self, db, callback):
        super().__init__(daemon=True)
        self._db = db
        self._callback = callback
        self._running = True

    def run(self):
        while self._running:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            due = self._db.get_due_reminders(now)
            for reminder in due:
                self._callback(reminder["message"])
                self._db.mark_reminder_delivered(reminder["id"])
            time.sleep(2)

    def stop(self):
        self._running = False
