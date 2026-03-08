from security.ai_guard import AIGuard


def test_ai_guard_filename_sanitize_and_limit():
    value = AIGuard.sanitize_filename("My Draft!! Final Version @2026")
    assert value == "my_draft_final_version_2026"

    long_value = AIGuard.sanitize_filename("a" * 80)
    assert len(long_value) == 50


def test_ai_guard_confirmation_and_tts_threshold():
    assert AIGuard.requires_confirmation("script.py") is True
    assert AIGuard.requires_confirmation("notes.txt") is False
    assert AIGuard.should_speak_full_output("short output") is True
    assert AIGuard.should_speak_full_output("x" * 401) is False
