from __future__ import annotations

from typing import Any

from jarvis.core.agent import Agent
from jarvis.core.task import TASK_STATUS_DONE, TASK_STATUS_FAILED, TASK_STATUS_RUNNING, Task


class AsyncExecutor:
    async def execute(self, task: Task, agent: Agent, context: dict[str, Any]) -> dict[str, Any]:
        task.status = TASK_STATUS_RUNNING
        try:
            result = await agent.execute(
                {
                    "id": task.id,
                    "intent": task.intent,
                    "params": task.params,
                    "dependencies": task.dependencies,
                    "status": task.status,
                },
                context,
            )
            task.status = TASK_STATUS_DONE
            return {"task_id": task.id, "status": task.status, "result": result}
        except Exception as exc:
            task.status = TASK_STATUS_FAILED
            return {"task_id": task.id, "status": task.status, "error": str(exc)}
