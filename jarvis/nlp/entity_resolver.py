from __future__ import annotations

import re


class EntityResolver:
    def __init__(self, mapping: dict[str, str] | None = None) -> None:
        self.mapping = mapping or {
            "yt": "youtube",
            "gh": "github",
            "mail": "gmail",
            "gmail": "https://mail.google.com",
        }

    def resolve_segment(self, segment: str) -> str:
        parts = re.split(r"(\W+)", segment)
        resolved_parts: list[str] = []
        for part in parts:
            resolved_parts.append(self.mapping.get(part.lower(), part))
        return "".join(resolved_parts)


def resolve_entities(segment: str) -> dict[str, str]:
    entities: dict[str, str] = {}
    timer_match = re.search(r"(\d+)\s*(seconds?|minutes?|hours?)", segment, flags=re.IGNORECASE)
    if timer_match:
        entities["duration"] = f"{timer_match.group(1)} {timer_match.group(2).lower()}"
    return entities
