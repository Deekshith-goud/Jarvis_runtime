from __future__ import annotations

from jarvis.core.orchestrator import Orchestrator


class VoiceInterface:
    def __init__(self, orchestrator: Orchestrator) -> None:
        self.orchestrator = orchestrator

    async def handle(self, transcript: str) -> dict:
        return await self.orchestrator.handle_command(transcript, context={"interface": "voice"})
