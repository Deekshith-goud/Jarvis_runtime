from core.entity_resolver import resolve_entity
from core.entity_registry import EntityRegistry


def test_resolve_entity_exact_prefix_fuzzy_and_miss():
    known = ["youtube", "google", "notepad"]

    assert resolve_entity("google", known) == ("google", 1.0)
    assert resolve_entity("you", known)[0] == "youtube"
    assert resolve_entity("youtub", known)[0] == "youtube"
    assert resolve_entity("something-else", known) == (None, 0.0)


def test_entity_registry_alias_and_fuzzy(no_user_config):
    registry = EntityRegistry()

    assert registry.resolve("yt") == ("website", "https://youtube.com")
    assert registry.resolve("youtub") == ("website", "https://youtube.com")
