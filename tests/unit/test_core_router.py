import asyncio

from jarvis.core.router import JarvisRouter


class StubClassifier:
    def __init__(self, intent: str, confidence: float) -> None:
        self.intent = intent
        self.confidence = confidence

    def classify(self, text: str):
        return self.intent, self.confidence


def test_router_deterministic_actions_for_youtube_and_timer():
    router = JarvisRouter(classifier=StubClassifier(intent="", confidence=0.0))

    result = asyncio.run(
        router.route(
            {
                "text": "open youtube and set timer 5 minutes",
                "segments": ["open youtube", "set timer 5 minutes"],
            }
        )
    )

    assert result["actions"] == [
        {"intent": "open_youtube"},
        {"intent": "set_timer", "params": {"duration": 300}},
    ]
    assert result["provider"] == "deterministic"


def test_router_uses_fasttext_before_llm():
    router = JarvisRouter(classifier=StubClassifier(intent="task", confidence=0.95))

    result = asyncio.run(router.route({"text": "please plan groceries", "segments": ["please plan groceries"]}))

    assert result["actions"] == [{"intent": "create_task", "params": {"text": "please plan groceries"}}]
    assert result["provider"] == "deterministic"


def test_router_selects_codex_for_code_tasks():
    router = JarvisRouter(classifier=StubClassifier(intent="", confidence=0.0))

    result = asyncio.run(router.route({"text": "fix this python bug in my script"}))

    assert result["provider"] == "codex"
    assert result["actions"][0]["intent"] == "code_task"


def test_router_uses_legacy_bridge_for_macro_full_command():
    router = JarvisRouter(classifier=StubClassifier(intent="", confidence=0.0))
    result = asyncio.run(router.route({"text": "create macro demo open youtube and set timer for 5 minutes"}))
    assert result["provider"] == "deterministic"
    assert result["actions"] == [
        {
            "intent": "legacy_command",
            "params": {"text": "create macro demo open youtube and set timer for 5 minutes"},
        }
    ]


def test_router_avoids_false_timer_fasttext_and_falls_back_to_legacy():
    router = JarvisRouter(classifier=StubClassifier(intent="timer", confidence=0.95))
    result = asyncio.run(router.route({"text": "remind me in 5 minutes to stretch", "segments": ["remind me in 5 minutes to stretch"]}))
    assert result["actions"] == [
        {
            "intent": "legacy_command",
            "params": {"text": "remind me in 5 minutes to stretch"},
        }
    ]
