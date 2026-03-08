from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any


class EventLogger:
    def __init__(self, storage: str = "jsonl", path: str | Path = "logs/jarvis_events.jsonl") -> None:
        self.storage = storage.lower()
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if self.storage == "sqlite":
            self._init_sqlite()
        elif self.storage != "jsonl":
            raise ValueError("storage must be 'jsonl' or 'sqlite'")

    def log_event(self, record: dict[str, Any]) -> None:
        if self.storage == "sqlite":
            self._log_sqlite(record)
        else:
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path.as_posix())

    def _init_sqlite(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event TEXT NOT NULL,
                    task_id TEXT,
                    intent TEXT,
                    agent TEXT,
                    timestamp TEXT NOT NULL,
                    payload TEXT
                )
                """
            )
            conn.commit()

    def _log_sqlite(self, record: dict[str, Any]) -> None:
        payload = dict(record)
        for key in ("event", "task_id", "intent", "agent", "timestamp"):
            payload.pop(key, None)
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO events (event, task_id, intent, agent, timestamp, payload)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    record.get("event", ""),
                    str(record.get("task_id", "")),
                    record.get("intent"),
                    record.get("agent"),
                    record.get("timestamp", ""),
                    json.dumps(payload, ensure_ascii=False, default=str),
                ),
            )
            conn.commit()
