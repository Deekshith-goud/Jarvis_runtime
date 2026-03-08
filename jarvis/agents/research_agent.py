from __future__ import annotations

import asyncio
from typing import Any

from jarvis.core.agent import Agent


class ResearchAgent(Agent):
    name = "research_agent"
    description = "Handles research and reasoning tasks."
    capabilities = ["research_topic", "summarize_text", "answer_question"]

    def can_handle(self, intent: str) -> bool:
        return intent in self.capabilities

    async def execute(self, task: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        intent = str(task.get("intent", ""))
        params = task.get("params", {}) or {}
        provider = self._select_provider(intent, params)
        await asyncio.sleep(0)
        response_text = self._build_response_text(intent, params, provider)
        return {
            "agent": self.name,
            "intent": intent,
            "provider": provider,
            "response": response_text,
            "status": "accepted",
        }

    def _select_provider(self, intent: str, params: dict[str, Any]) -> str:
        if intent == "research_topic":
            topic = str(params.get("topic", "")).strip()
            return "gemini" if len(topic.split()) > 6 else "groq"
        if intent == "summarize_text":
            text = str(params.get("text", "")).strip()
            return "gemini" if len(text) > 800 else "groq"
        if intent == "answer_question":
            question = str(params.get("question", "")).strip()
            return "gemini" if len(question.split()) > 20 else "groq"
        return "groq"

    @staticmethod
    def _build_response_text(intent: str, params: dict[str, Any], provider: str) -> str:
        if intent == "research_topic":
            topic = str(params.get("topic", "")).strip() or "requested topic"
            return f"[{provider}] Research summary prepared for: {topic}."
        if intent == "summarize_text":
            return f"[{provider}] Summary generated from provided text."
        if intent == "answer_question":
            question = str(params.get("question", "")).strip() or "requested question"
            return f"[{provider}] Answer drafted for: {question}."
        return f"[{provider}] Reasoning completed."
