from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

TASK_STATUS_PENDING = "pending"
TASK_STATUS_RUNNING = "running"
TASK_STATUS_DONE = "done"
TASK_STATUS_FAILED = "failed"


@dataclass(slots=True)
class Task:
    id: str
    intent: str
    params: dict[str, Any] = field(default_factory=dict)
    dependencies: list[str] = field(default_factory=list)
    status: str = TASK_STATUS_PENDING


@dataclass(slots=True)
class TaskGraph:
    tasks: dict[str, Task] = field(default_factory=dict)

    def add_task(self, task: Task) -> None:
        self.tasks[task.id] = task

    def get_task(self, task_id: str) -> Task:
        return self.tasks[task_id]

    def dependency_count(self, task_id: str) -> int:
        return len(self.tasks[task_id].dependencies)
