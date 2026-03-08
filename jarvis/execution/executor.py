from __future__ import annotations

import asyncio
import logging
from datetime import UTC, datetime
from typing import Any, Callable

from jarvis.core.agent_registry import AgentRegistry
from jarvis.core.context import ContextInjector
from jarvis.core.events import EventLogger
from jarvis.core.safety import SafetyValidator
from jarvis.core.task_graph import TaskGraph, TaskNode


class Executor:
    def __init__(
        self,
        registry: AgentRegistry,
        logger: logging.Logger | None = None,
        event_hook: Callable[[dict[str, Any]], None] | None = None,
        event_logger: EventLogger | None = None,
        safety_validator: SafetyValidator | None = None,
        context_injector: ContextInjector | None = None,
    ) -> None:
        self.registry = registry
        self.logger = logger or logging.getLogger(__name__)
        self.event_hook = event_hook
        self.event_logger = event_logger
        self.safety_validator = safety_validator or SafetyValidator()
        self.context_injector = context_injector or ContextInjector()

    async def execute(self, graph: TaskGraph, context: dict[str, Any] | None = None) -> dict[str, Any]:
        run_context = self.context_injector.build(context)
        results: dict[str, Any] = {}

        for task in graph.get_all_tasks():
            self._emit("task_created", task, {"dependencies": list(task.dependencies)})

        while graph.has_unfinished_tasks():
            ready_tasks = graph.get_ready_tasks()
            if not ready_tasks:
                raise ValueError("TaskGraph is blocked: no ready tasks but unfinished tasks remain")

            batch = [asyncio.create_task(self._run_task(graph, task, run_context)) for task in ready_tasks]
            batch_results = await asyncio.gather(*batch)
            for result in batch_results:
                results[result["task_id"]] = result

        return results

    async def _run_task(self, graph: TaskGraph, task: TaskNode, context: dict[str, Any]) -> dict[str, Any]:
        is_safe, reason = self.safety_validator.validate_task(task)
        if not is_safe:
            graph.mark_failed(task.id)
            result = {"task_id": task.id, "status": "failed", "error": reason}
            self._emit("task_failed", task, {**result, "safety_violation": True})
            return result

        agent = self.registry.find_agent_by_intent(task.intent)
        if agent is None:
            graph.mark_failed(task.id)
            result = {"task_id": task.id, "status": "failed", "error": f"No agent found for intent '{task.intent}'"}
            self._emit("task_failed", task, result)
            return result

        agent_name = getattr(agent, "__class__", type(agent)).__name__
        self._emit("agent_selected", task, {"agent": agent_name})
        graph.mark_running(task.id)
        self._emit("task_started", task, {"agent": agent_name})

        try:
            payload = {
                "id": task.id,
                "intent": task.intent,
                "params": task.params,
                "dependencies": task.dependencies,
                "status": task.status,
            }
            output = await agent.execute(payload, context)
            graph.mark_complete(task.id)
            result = {"task_id": task.id, "status": "complete", "result": output}
            self._emit("task_completed", task, result)
            return result
        except Exception as exc:
            graph.mark_failed(task.id)
            result = {"task_id": task.id, "status": "failed", "error": str(exc)}
            self._emit("task_failed", task, result)
            return result

    def _emit(self, event: str, task: TaskNode, payload: dict[str, Any]) -> None:
        record = {
            "event": event,
            "task_id": task.id,
            "intent": task.intent,
            "timestamp": datetime.now(UTC).isoformat(),
            **payload,
        }
        self.logger.info("executor_event=%s", record)
        if self.event_logger:
            self.event_logger.log_event(record)
        if self.event_hook:
            self.event_hook(record)
