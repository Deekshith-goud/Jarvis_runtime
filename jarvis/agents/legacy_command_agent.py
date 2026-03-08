from __future__ import annotations

from typing import Any

from jarvis.core.agent import Agent


class LegacyCommandAgent(Agent):
    name = "legacy_command_agent"
    description = "Compatibility bridge for legacy command behaviors."
    capabilities = ["legacy_command"]

    def can_handle(self, intent: str) -> bool:
        return intent in self.capabilities

    async def execute(self, task: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        # Lazy import avoids initialization cycles between legacy core and jarvis packages.
        from core.command_router import route_command

        params = task.get("params", {}) or {}
        text = str(params.get("text", "")).strip()
        if not text:
            return {
                "agent": self.name,
                "intent": "legacy_command",
                "status": "completed",
                "message": "I did not understand the command.",
                "params": params,
            }

        legacy = route_command(text)
        return {
            "agent": self.name,
            "intent": "legacy_command",
            "status": "completed",
            "legacy_success": bool(legacy.success),
            "category": legacy.category,
            "message": legacy.message,
            "params": params,
        }
