from __future__ import annotations

from typing import Any

from jarvis.core.agent import Agent
from skills.web_skill import handle_web


class BrowserAgent(Agent):
    name = "browser_agent"
    description = "Handles web browsing tasks."
    capabilities = ["search_web", "open_youtube", "open_website"]

    def can_handle(self, intent: str) -> bool:
        return intent in self.capabilities

    async def execute(self, task: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        intent = task.get("intent", "")
        params = task.get("params", {}) or {}
        if intent == "open_youtube":
            message = handle_web("open youtube")
        elif intent == "search_web":
            query = params.get("query") or params.get("text") or ""
            message = handle_web(f"search {query}".strip())
        else:
            target = params.get("target") or params.get("text") or ""
            message = handle_web(f"open {target}".strip())
        return {
            "agent": self.name,
            "intent": intent,
            "status": "completed",
            "message": message,
            "params": params,
        }
