from __future__ import annotations

from jarvis.core.orchestrator import Orchestrator


class CLIInterface:
    def __init__(self, orchestrator: Orchestrator) -> None:
        self.orchestrator = orchestrator

    async def handle(self, command: str) -> dict:
        return await self.orchestrator.handle_command(command, context={"interface": "cli"})
