from __future__ import annotations

import asyncio
from typing import Any, Callable

from jarvis.core.agent_registry import AgentRegistry
from jarvis.core.task import TaskGraph
from jarvis.execution.async_executor import AsyncExecutor


class TaskGraphEngine:
    def __init__(
        self,
        agent_registry: AgentRegistry,
        executor: AsyncExecutor | None = None,
    ) -> None:
        self.agent_registry = agent_registry
        self.executor = executor or AsyncExecutor()

    async def execute(
        self,
        graph: TaskGraph,
        context: dict[str, Any] | None = None,
        agent_registry: AgentRegistry | None = None,
        on_task_update: Callable[[dict[str, Any]], None] | None = None,
    ) -> dict[str, Any]:
        """Execute TaskGraph with async parallel batches for dependency-free tasks."""
        run_context = context or {}
        registry = agent_registry or self.agent_registry
        pending = set(graph.tasks.keys())
        completed: set[str] = set()
        results: dict[str, Any] = {}

        while pending:
            ready = [
                graph.get_task(task_id)
                for task_id in pending
                if all(dep_id in completed for dep_id in graph.get_task(task_id).dependencies)
            ]
            if not ready:
                unresolved = ", ".join(sorted(pending))
                raise ValueError(f"Cyclic or unresolved dependencies among tasks: {unresolved}")

            batch = []
            for task in ready:
                agent = registry.get_agent_for_intent(task.intent)
                if agent is None:
                    results[task.id] = {
                        "task_id": task.id,
                        "status": "failed",
                        "error": f"No agent available for intent '{task.intent}'",
                    }
                    completed.add(task.id)
                    if on_task_update:
                        on_task_update(results[task.id])
                    continue
                if on_task_update:
                    on_task_update(
                        {
                            "task_id": task.id,
                            "status": "running",
                            "intent": task.intent,
                            "agent": agent.name,
                        }
                    )
                batch.append((task.id, asyncio.create_task(self.executor.execute(task, agent, run_context))))

            if batch:
                batch_results = await asyncio.gather(*(future for _, future in batch))
                for task_id, result in zip((task_id for task_id, _ in batch), batch_results):
                    results[task_id] = result
                    completed.add(task_id)
                    if on_task_update:
                        on_task_update(result)

            pending -= {task.id for task in ready}

        return results
