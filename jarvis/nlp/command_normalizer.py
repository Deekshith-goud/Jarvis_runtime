from __future__ import annotations

import re
from typing import Any

from jarvis.nlp.entity_resolver import EntityResolver
from jarvis.nlp.intent_classifier import FastTextIntentClassifier
from jarvis.nlp.segment_parser import split_segments


class CommandNormalizer:
    def __init__(
        self,
        segment_parser=split_segments,
        entity_resolver: EntityResolver | None = None,
        intent_classifier: FastTextIntentClassifier | None = None,
    ) -> None:
        self.segment_parser = segment_parser
        self.entity_resolver = entity_resolver or EntityResolver()
        self.intent_classifier = intent_classifier or FastTextIntentClassifier()

    def normalize(self, raw_text: str) -> dict[str, Any]:
        actions: list[dict[str, Any]] = []
        for segment in self.segment_parser(raw_text):
            resolved_segment = self.entity_resolver.resolve_segment(segment)
            intent, _ = self.intent_classifier.classify(resolved_segment)
            if intent == "unknown":
                continue
            action: dict[str, Any] = {"intent": intent}
            params = self._extract_params(intent, resolved_segment)
            if params:
                action["params"] = params
            actions.append(action)
        return {"actions": actions}

    def _extract_params(self, intent: str, segment: str) -> dict[str, Any]:
        params: dict[str, Any] = {}
        lower = segment.lower()
        if intent == "set_timer":
            seconds = self._duration_to_seconds(lower)
            if seconds is not None:
                params["duration"] = seconds
        elif intent == "open_website":
            target = re.sub(r"^(open|go to)\s+", "", segment, flags=re.IGNORECASE).strip()
            params["target"] = target
        elif intent == "open_app":
            target = re.sub(r"^(open|launch|start)\s+", "", segment, flags=re.IGNORECASE).strip()
            params["target"] = target
        elif intent in {"check_timer", "cancel_timer"}:
            return params
        elif intent == "search_web":
            query = re.sub(r"^search(?: the)?(?: web)?(?: for)?\s*", "", lower).strip()
            if query:
                params["query"] = query
            else:
                params["query"] = segment
        elif intent == "research_topic":
            topic = re.sub(r"^research(?: topic)?\s*", "", segment, flags=re.IGNORECASE).strip()
            params["topic"] = topic or segment
        elif intent == "summarize_text":
            text = re.sub(r"^summarize\s*", "", segment, flags=re.IGNORECASE).strip()
            params["text"] = text or segment
        elif intent == "answer_question":
            question = re.sub(r"^answer\s*", "", segment, flags=re.IGNORECASE).strip()
            params["question"] = question or segment
        elif intent in {"set_reminder", "create_task"}:
            params["text"] = segment
        return params

    @staticmethod
    def _duration_to_seconds(text: str) -> int | None:
        match = re.search(r"(\d+)\s*(second|seconds|minute|minutes|hour|hours)", text)
        if not match:
            return None
        value = int(match.group(1))
        unit = match.group(2)
        if unit.startswith("second"):
            return value
        if unit.startswith("minute"):
            return value * 60
        return value * 3600


def normalize_command(raw_text: str) -> dict[str, Any]:
    return CommandNormalizer().normalize(raw_text)
