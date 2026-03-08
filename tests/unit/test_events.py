import json
import sqlite3

from jarvis.core.events import EventLogger


def test_event_logger_writes_jsonl(isolated_cwd):
    path = isolated_cwd / "events.jsonl"
    logger = EventLogger(storage="jsonl", path=path)
    logger.log_event(
        {
            "event": "task_started",
            "task_id": "task2",
            "intent": "set_timer",
            "agent": "ProductivityAgent",
            "timestamp": "2026-03-05T00:00:00+00:00",
        }
    )

    content = path.read_text(encoding="utf-8").strip()
    record = json.loads(content)
    assert record["event"] == "task_started"
    assert record["agent"] == "ProductivityAgent"


def test_event_logger_writes_sqlite(isolated_cwd):
    path = isolated_cwd / "events.db"
    logger = EventLogger(storage="sqlite", path=path)
    logger.log_event(
        {
            "event": "task_failed",
            "task_id": "task4",
            "intent": "search_web",
            "agent": "BrowserAgent",
            "timestamp": "2026-03-05T00:00:00+00:00",
            "error": "network timeout",
        }
    )

    with sqlite3.connect(path.as_posix()) as conn:
        row = conn.execute("SELECT event, task_id, intent, agent, payload FROM events").fetchone()

    assert row[0] == "task_failed"
    assert row[1] == "task4"
    assert row[2] == "search_web"
    assert row[3] == "BrowserAgent"
    assert "network timeout" in row[4]
