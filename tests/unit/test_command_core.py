from core.command_normalizer import normalize_command
from core.command_result import CommandResult
from core.segment_parser import split_segments


def test_command_result_success_and_failure_factories():
    ok = CommandResult.success("done", "system", {"x": 1})
    err = CommandResult.failure("failed", "system")

    assert ok.success is True
    assert ok.message == "done"
    assert ok.metadata == {"x": 1}
    assert err.success is False
    assert err.metadata == {}


def test_normalize_command_basic_cleanup():
    original, normalized = normalize_command("   Open   YouTube   ")
    assert original == "   Open   YouTube   "
    assert normalized == "open youtube"


def test_normalize_command_duplicate_halves_reduced():
    _, normalized = normalize_command("runrun")
    assert normalized == "run"


def test_split_segments_multi_delimiter():
    segments = split_segments("open youtube, set timer and play music")
    assert segments == ["open youtube", "set timer", "play music"]
