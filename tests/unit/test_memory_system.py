from jarvis.memory.memory_system import JarvisMemory, LongTermMemory, SessionMemory, ShortTermMemory


def test_short_term_memory_tracks_current_command():
    memory = ShortTermMemory()
    memory.set_current_command({"text": "open youtube", "intent": "open_youtube"})

    assert memory.get_current_command() == {"text": "open youtube", "intent": "open_youtube"}

    memory.clear()
    assert memory.get_current_command() == {}


def test_session_memory_tracks_conversation_and_task_history():
    session = SessionMemory()
    session.add_turn("add task buy milk", "Task created")
    session.add_task_event({"task_id": "task1", "status": "complete"})

    assert session.get_last()["last_command"] == "add task buy milk"
    assert len(session.get_conversation_state()) == 1
    assert session.get_task_history()[0]["task_id"] == "task1"


def test_long_term_memory_persists_preferences_and_command_usage(isolated_cwd):
    db_path = isolated_cwd / "jarvis_memory.db"
    long_term = LongTermMemory(db_path=db_path)

    long_term.set_preference("theme", "light")
    long_term.record_command("open youtube")
    long_term.record_command("open youtube")
    long_term.record_command("set timer 5 minutes")

    assert long_term.get_preference("theme") == "light"
    commands = long_term.get_frequent_commands(limit=2)
    assert commands[0]["command"] == "open youtube"
    assert commands[0]["count"] == 2


def test_jarvis_memory_exposes_agent_context(isolated_cwd):
    long_term = LongTermMemory(db_path=isolated_cwd / "ctx.db")
    long_term.record_command("open youtube")

    short_term = ShortTermMemory()
    short_term.set_current_command({"text": "open youtube"})

    session = SessionMemory()
    session.add_turn("open youtube", "Opening YouTube")

    memory = JarvisMemory(short_term=short_term, session=session, long_term=long_term)
    context = memory.build_context()

    assert context["memory"]["short_term"]["text"] == "open youtube"
    assert context["memory"]["session"]["conversation_state"][0]["user_input"] == "open youtube"
    assert context["memory"]["long_term"]["frequent_commands"][0]["command"] == "open youtube"
