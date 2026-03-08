from __future__ import annotations

import asyncio
from typing import Any, Protocol

from jarvis.core.agent import Agent


class CodexClient(Protocol):
    async def generate(self, prompt: str, metadata: dict[str, Any]) -> str: ...


class LocalCodexStub:
    async def generate(self, prompt: str, metadata: dict[str, Any]) -> str:
        await asyncio.sleep(0)
        language = metadata.get("language", "text")
        return f"[codex:{language}] Generated response for: {prompt}"


class CodeAgent(Agent):
    name = "code_agent"
    description = "Handles programming and coding tasks via Codex."
    capabilities = ["generate_code", "fix_code", "explain_code", "write_script"]

    def __init__(self, codex_client: CodexClient | None = None) -> None:
        self.codex_client = codex_client or LocalCodexStub()

    def can_handle(self, intent: str) -> bool:
        return intent in self.capabilities

    async def execute(self, task: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        intent = str(task.get("intent", "")).strip()
        params = task.get("params", {}) or {}
        prompt = self._build_prompt(intent, params)
        text = await self.codex_client.generate(
            prompt=prompt,
            metadata={"intent": intent, "language": params.get("language", "text"), "task_id": task.get("id")},
        )
        return {
            "agent": self.name,
            "intent": intent,
            "provider": "codex",
            "response": text,
            "status": "accepted",
        }

    @staticmethod
    def _build_prompt(intent: str, params: dict[str, Any]) -> str:
        language = str(params.get("language", "")).strip()
        content_task = str(params.get("task", "")).strip()
        code = str(params.get("code", "")).strip()
        script_goal = str(params.get("goal", "")).strip()
        if intent == "generate_code":
            return f"Generate {language or 'code'}: {content_task}".strip()
        if intent == "fix_code":
            return f"Fix this {language or ''} code:\n{code}".strip()
        if intent == "explain_code":
            return f"Explain this {language or ''} code:\n{code}".strip()
        if intent == "write_script":
            return f"Write a {language or ''} script for: {script_goal or content_task}".strip()
        return content_task or "Handle code task"
