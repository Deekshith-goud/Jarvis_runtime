from __future__ import annotations

from typing import Any

from jarvis.core.task_graph import TaskGraph, TaskNode
from jarvis.nlp.command_normalizer import normalize_command


class Planner:
    _FOLLOW_UP_INTENTS = {"summarize_results", "analyze_results", "explain_results"}
    _PRODUCER_INTENTS = {"search_web", "research_query", "fetch_results", "get_documents"}

    def create_plan(self, parsed_command: dict[str, Any]) -> TaskGraph:
        actions = parsed_command.get("actions")
        if not isinstance(actions, list):
            actions = normalize_command(str(parsed_command.get("text", ""))).get("actions", [])
        graph = TaskGraph()
        last_producer_task_id: str | None = None

        for index, action in enumerate(actions, start=1):
            intent = str(action.get("intent", "")).strip()
            params = action.get("params", {}) or {}
            task_id = f"task{index}"
            dependencies: list[str] = []

            if intent in self._FOLLOW_UP_INTENTS and last_producer_task_id:
                dependencies.append(last_producer_task_id)

            task = TaskNode(id=task_id, intent=intent, params=params, dependencies=dependencies)
            graph.add_task(task)

            if intent in self._PRODUCER_INTENTS:
                last_producer_task_id = task_id

        return graph

    def build_task_graph(self, command: str) -> TaskGraph:
        return self.create_plan({"text": command})
