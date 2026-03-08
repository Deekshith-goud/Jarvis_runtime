from __future__ import annotations

from typing import Any

from jarvis.nlp.segment_parser import split_segments
from nlu.intent_classifier import IntentClassifier


class JarvisRouter:
    def __init__(self, classifier: Any | None = None, fasttext_threshold: float = 0.7) -> None:
        self.classifier = classifier or IntentClassifier()
        self.fasttext_threshold = fasttext_threshold

    async def route(self, parsed_command: dict[str, Any]) -> dict[str, Any]:
        text = str(parsed_command.get("text", "")).strip()
        if self._should_use_legacy_full_command(text):
            return {"provider": "deterministic", "actions": [{"intent": "legacy_command", "params": {"text": text}}]}

        segments = parsed_command.get("segments")
        if not isinstance(segments, list) or not segments:
            segments = split_segments(text)

        actions: list[dict[str, Any]] = []
        unresolved: list[str] = []
        for segment in segments:
            if self._should_use_legacy_segment(segment):
                actions.append({"intent": "legacy_command", "params": {"text": segment}})
                continue
            resolved = self._deterministic_action(segment)
            if resolved:
                actions.append(resolved)
                continue
            ft = self._fasttext_action(segment)
            if ft:
                actions.append(ft)
                continue
            unresolved.append(segment)

        provider = "deterministic" if not unresolved else self._select_reasoning_provider(text)
        if unresolved:
            actions.extend(await self._reason_with_provider(provider, unresolved))
        return {"provider": provider, "actions": actions}

    def _deterministic_action(self, segment: str) -> dict[str, Any] | None:
        lower = segment.lower().strip()
        if "youtube" in lower and ("open" in lower or "play" in lower):
            return {"intent": "open_youtube"}
        if "timer" in lower and ("set" in lower or "for " in lower):
            seconds = self._duration_to_seconds(lower)
            return {"intent": "set_timer", "params": {"duration": seconds}} if seconds else {"intent": "set_timer"}
        if lower.startswith("search"):
            query = lower.replace("search", "", 1).replace("web", "", 1).replace("for", "", 1).strip()
            return {"intent": "search_web", "params": {"query": query}} if query else {"intent": "search_web"}
        return None

    def _fasttext_action(self, segment: str) -> dict[str, Any] | None:
        intent, confidence = self.classifier.classify(segment)
        if confidence < self.fasttext_threshold:
            return None
        mapping = {"timer": "set_timer", "task": "create_task", "search": "search_web", "code": "code_task"}
        mapped = mapping.get(intent)
        if not mapped:
            return None
        if mapped == "set_timer" and "timer" not in segment.lower():
            return None
        return {"intent": mapped, "params": {"text": segment}}

    @staticmethod
    def _select_reasoning_provider(text: str) -> str:
        lower = text.lower()
        if any(t in lower for t in ("code", "python", "refactor", "bug")):
            return "codex"
        if any(t in lower for t in ("deep", "research", "architecture", "compare")):
            return "gemini"
        if any(t in lower for t in ("quick", "fast", "brief", "summarize")):
            return "groq"
        return "cloudflare_workers_ai"

    async def _reason_with_provider(self, provider: str, segments: list[str]) -> list[dict[str, Any]]:
        if provider == "codex":
            return [{"intent": "code_task", "params": {"text": segment, "provider": provider}} for segment in segments]
        # Route unresolved, non-coding commands through legacy bridge behavior
        # so feature-complete command handling remains available inside jarvis flow.
        return [{"intent": "legacy_command", "params": {"text": segment, "provider": provider}} for segment in segments]

    @staticmethod
    def _should_use_legacy_full_command(text: str) -> bool:
        lower = text.lower().strip()
        return (
            lower.startswith("create macro ")
            or lower.startswith("delete macro ")
            or lower == "list macros"
            or lower.startswith("save as ")
            or lower in {"save it", "save that", "create document"}
            or lower in {"more", "tell me more", "explain more"}
        )

    @staticmethod
    def _should_use_legacy_segment(segment: str) -> bool:
        lower = segment.lower().strip()
        prefixes = (
            "delete macro ",
            "list macros",
            "good morning",
            "morning briefing",
            "enter focus mode",
            "exit focus mode",
            "start work session",
            "end work session",
            "how long have i worked",
            "show analytics",
            "productivity report",
            "performance stats",
            "remember that",
            "remember this",
            "what do you remember",
            "list memories",
            "list memory",
            "delete memory",
            "take screenshot",
            "screenshot",
            "read clipboard",
            "copy ",
            "paste",
            "remind me in ",
            "what was i doing",
        )
        return lower.startswith(prefixes)

    @staticmethod
    def _duration_to_seconds(text: str) -> int | None:
        import re

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
