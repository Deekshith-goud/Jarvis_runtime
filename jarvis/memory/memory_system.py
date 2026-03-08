from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


@dataclass
class ShortTermMemory:
    current_command: dict[str, Any] = field(default_factory=dict)

    def set_current_command(self, command_state: dict[str, Any]) -> None:
        self.current_command = dict(command_state)

    def get_current_command(self) -> dict[str, Any]:
        return dict(self.current_command)

    def clear(self) -> None:
        self.current_command.clear()


class SessionMemory:
    def __init__(self) -> None:
        self._conversation: list[dict[str, Any]] = []
        self._task_history: list[dict[str, Any]] = []
        self._last_command = ""
        self._last_response = ""
        self._last_task = ""

    def add_turn(self, user_input: str, assistant_output: str) -> None:
        self._last_command = user_input
        self._last_response = assistant_output
        if "task" in user_input.lower():
            self._last_task = user_input
        self._conversation.append(
            {
                "timestamp": _utc_now(),
                "user_input": user_input,
                "assistant_output": assistant_output,
            }
        )

    def add_task_event(self, event: dict[str, Any]) -> None:
        self._task_history.append({"timestamp": _utc_now(), **event})

    def get_conversation_state(self) -> list[dict[str, Any]]:
        return list(self._conversation)

    def get_task_history(self) -> list[dict[str, Any]]:
        return list(self._task_history)

    def update(self, command: str, response: str) -> None:
        self.add_turn(command, response)

    def get_last(self) -> dict[str, str]:
        return {
            "last_command": self._last_command,
            "last_response": self._last_response,
            "last_task": self._last_task,
        }

    def clear(self) -> None:
        self._conversation.clear()
        self._task_history.clear()
        self._last_command = ""
        self._last_response = ""
        self._last_task = ""


class LongTermMemory:
    def __init__(self, db_path: str | Path = "jarvis_memory.db") -> None:
        self.db_path = str(db_path)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _initialize(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS user_preferences (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS command_usage (
                    command TEXT PRIMARY KEY,
                    count INTEGER NOT NULL DEFAULT 0,
                    last_used_at TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def set_preference(self, key: str, value: str) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO user_preferences (key, value, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    value=excluded.value,
                    updated_at=excluded.updated_at
                """,
                (key, value, _utc_now()),
            )
            conn.commit()

    def get_preference(self, key: str) -> str | None:
        with self._connect() as conn:
            row = conn.execute("SELECT value FROM user_preferences WHERE key = ?", (key,)).fetchone()
        return None if row is None else str(row["value"])

    def record_command(self, command: str) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO command_usage (command, count, last_used_at)
                VALUES (?, 1, ?)
                ON CONFLICT(command) DO UPDATE SET
                    count = command_usage.count + 1,
                    last_used_at = excluded.last_used_at
                """,
                (command, _utc_now()),
            )
            conn.commit()

    def get_frequent_commands(self, limit: int = 10) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT command, count, last_used_at
                FROM command_usage
                ORDER BY count DESC, last_used_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]


class JarvisMemory:
    def __init__(
        self,
        short_term: ShortTermMemory | None = None,
        session: SessionMemory | None = None,
        long_term: LongTermMemory | None = None,
    ) -> None:
        self.short_term = short_term or ShortTermMemory()
        self.session = session or SessionMemory()
        self.long_term = long_term or LongTermMemory()

    def build_context(self) -> dict[str, Any]:
        return {
            "memory": {
                "short_term": self.short_term.get_current_command(),
                "session": {
                    "conversation_state": self.session.get_conversation_state(),
                    "task_history": self.session.get_task_history(),
                },
                "long_term": {"frequent_commands": self.long_term.get_frequent_commands()},
            }
        }
