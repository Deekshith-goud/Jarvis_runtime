from jarvis.nlp.command_normalizer import CommandNormalizer, normalize_command
from jarvis.nlp.entity_resolver import EntityResolver
from jarvis.nlp.intent_classifier import FastTextIntentClassifier
from jarvis.nlp.segment_parser import split_segments


class StubFastText:
    def __init__(self, intent: str = "unknown", confidence: float = 0.0) -> None:
        self.intent = intent
        self.confidence = confidence

    def classify(self, text: str):
        return self.intent, self.confidence


def test_segment_parser_splits_multi_action_command():
    result = split_segments("open youtube and set timer 5 minutes, also search web for python then open gh")
    assert result == ["open youtube", "set timer 5 minutes", "search web for python", "open gh"]


def test_entity_resolver_maps_informal_entities():
    resolver = EntityResolver()
    assert resolver.resolve_segment("open yt") == "open youtube"
    assert resolver.resolve_segment("open gh") == "open github"
    assert resolver.resolve_segment("open mail") == "open gmail"


def test_intent_classifier_detects_timer_intent():
    classifier = FastTextIntentClassifier(classifier=StubFastText(intent="unknown", confidence=0.0))
    intent, confidence = classifier.classify("set timer 5 minutes")
    assert intent == "set_timer"
    assert confidence == 1.0


def test_command_normalizer_returns_structured_actions():
    output = normalize_command("open youtube and set timer for 5 minutes")

    assert output == {
        "actions": [
            {"intent": "open_youtube"},
            {"intent": "set_timer", "params": {"duration": 300}},
        ]
    }


def test_command_normalizer_uses_fasttext_when_needed():
    normalizer = CommandNormalizer(
        intent_classifier=FastTextIntentClassifier(classifier=StubFastText(intent="task", confidence=0.9))
    )
    output = normalizer.normalize("please organize groceries")

    assert output == {"actions": [{"intent": "create_task", "params": {"text": "please organize groceries"}}]}
