from __future__ import annotations

from jarvis.agents.base_agent import KeywordAgent


class MediaAgent(KeywordAgent):
    def __init__(self) -> None:
        super().__init__(
            name="media_agent",
            description="Handles media playback commands.",
            capabilities=["youtube", "music"],
            intents={"play_media", "open_youtube"},
        )
