from __future__ import annotations

from typing import Any, Iterable

from jarvis.core.agent import Agent


class AgentRegistry:
    def __init__(self, agents: Iterable[Agent] | None = None) -> None:
        self._agents: list[Any] = []
        if agents:
            for agent in agents:
                self.register(agent)

    def register(self, agent: Any) -> None:
        self._agents.append(agent)

    def unregister(self, agent_name: str) -> None:
        self._agents = [agent for agent in self._agents if getattr(agent, "name", None) != agent_name]

    def get_all_agents(self) -> list[Any]:
        return list(self._agents)

    def find_agent_by_intent(self, intent: str) -> Any | None:
        for agent in self._agents:
            can_handle = getattr(agent, "can_handle", None)
            if callable(can_handle) and can_handle(intent):
                return agent
            capabilities = getattr(agent, "capabilities", None)
            if isinstance(capabilities, list) and intent in capabilities:
                return agent
        return None

    # Backward-compatible aliases.
    def list_agents(self) -> list[Agent]:
        return self.get_all_agents()

    def get_agent_for_intent(self, intent: str) -> Agent | None:
        return self.find_agent_by_intent(intent)
