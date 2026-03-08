from __future__ import annotations

from nlu.intent_classifier import IntentClassifier as LegacyFastTextClassifier


class FastTextIntentClassifier:
    def __init__(self, classifier: LegacyFastTextClassifier | None = None, threshold: float = 0.7) -> None:
        self.classifier = classifier or LegacyFastTextClassifier()
        self.threshold = threshold

    def classify(self, text: str) -> tuple[str, float]:
        keyword = self._keyword_intent(text)
        if keyword:
            return keyword, 1.0
        label, confidence = self.classifier.classify(text)
        if confidence < self.threshold:
            return "unknown", confidence
        return self._map_fasttext_label(label), confidence

    def predict(self, segment: str) -> str:
        intent, _ = self.classify(segment)
        return intent

    @staticmethod
    def _keyword_intent(text: str) -> str | None:
        lower = text.lower()
        if "check timer" in lower or "timer status" in lower or "how much time" in lower:
            return "check_timer"
        if "cancel timer" in lower or "stop timer" in lower:
            return "cancel_timer"
        if lower.startswith("research"):
            return "research_topic"
        if lower.startswith("summarize"):
            return "summarize_text"
        if lower.startswith("answer"):
            return "answer_question"
        if "youtube" in lower and ("open" in lower or "play" in lower):
            return "open_youtube"
        if "timer" in lower and ("set" in lower or "for " in lower):
            return "set_timer"
        if "remind me" in lower:
            return "set_reminder"
        if "task" in lower and ("create" in lower or "add" in lower):
            return "create_task"
        if "search" in lower:
            return "search_web"
        if "open " in lower and any(token in lower for token in (".com", ".org", ".net", "http://", "https://")):
            return "open_website"
        if "open " in lower and any(token in lower for token in ("youtube", "gmail", "github", "google")):
            return "open_website"
        if "open " in lower:
            return "open_app"
        return None

    @staticmethod
    def _map_fasttext_label(label: str) -> str:
        mapping = {
            "timer": "set_timer",
            "task": "create_task",
            "search": "search_web",
            "reminder": "set_reminder",
            "open_youtube": "open_youtube",
            "open_app": "open_app",
            "research": "research_topic",
            "summarize": "summarize_text",
            "unknown": "unknown",
        }
        return mapping.get(label, "unknown")
