from jarvis.memory.memory_system import SessionMemory
from storage.database import DatabaseManager


def test_session_memory_tracks_last_task():
    sm = SessionMemory()
    sm.update("add task finish architecture doc", "added")
    payload = sm.get_last()

    assert payload["last_command"] == "add task finish architecture doc"
    assert payload["last_response"] == "added"
    assert "task" in payload["last_task"]


def test_database_manager_task_and_macro_lifecycle(isolated_cwd):
    db = DatabaseManager()

    assert db.add_task("finish migration plan") is True
    assert db.add_task("finish migration plan") is False

    pending = db.list_tasks()
    assert len(pending) == 1
    task_id = pending[0]["id"]

    db.mark_task_done(task_id)
    assert db.get_last_pending_task() is None

    assert db.create_macro("study_mode", "open notion; open youtube") is True
    assert db.get_macro("study_mode") == "open notion; open youtube"
    assert db.delete_macro("study_mode") is True
