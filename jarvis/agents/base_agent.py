from __future__ import annotations

import asyncio
from typing import Any

from jarvis.core.agent import Agent


class KeywordAgent(Agent):
    def __init__(
        self,
        name: str,
        description: str,
        capabilities: list[str],
        intents: set[str],
    ) -> None:
        self.name = name
        self.description = description
        self.capabilities = capabilities
        self._intents = intents

    def can_handle(self, intent: str) -> bool:
        return intent in self._intents

    async def execute(self, task: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        # Placeholder execution to keep architecture stable while APIs are stubbed.
        await asyncio.sleep(0)
        return {
            "agent": self.name,
            "intent": task["intent"],
            "handled": True,
            "params": task.get("params", {}),
        }
