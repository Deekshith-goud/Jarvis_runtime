from __future__ import annotations

import re


def split_segments(command: str) -> list[str]:
    if not command or not command.strip():
        return []
    normalized = re.sub(r"\s+", " ", command.strip().lower())
    raw_parts = re.split(r"\s*(?:,|\band\b|\bthen\b|\balso\b)\s*", normalized, flags=re.IGNORECASE)
    return [part.strip() for part in raw_parts if part and part.strip()]
