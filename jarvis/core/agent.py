from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class Agent(ABC):
    name: str = ""
    description: str = ""
    capabilities: list[str] = []

    @abstractmethod
    def can_handle(self, intent: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def execute(self, task: dict[str, Any], context: dict[str, Any]) -> Any:
        raise NotImplementedError
