from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

STATUS_PENDING = "pending"
STATUS_RUNNING = "running"
STATUS_COMPLETE = "complete"
STATUS_FAILED = "failed"


@dataclass(slots=True)
class TaskNode:
    id: str
    intent: str
    params: dict[str, Any] = field(default_factory=dict)
    dependencies: list[str] = field(default_factory=list)
    status: str = STATUS_PENDING


class TaskGraph:
    def __init__(self) -> None:
        self._tasks: dict[str, TaskNode] = {}

    def add_task(self, task: TaskNode) -> None:
        if task.id in self._tasks:
            raise ValueError(f"Task with id '{task.id}' already exists")
        self._tasks[task.id] = task

    def get_ready_tasks(self) -> list[TaskNode]:
        ready: list[TaskNode] = []
        for task in self._tasks.values():
            if task.status != STATUS_PENDING:
                continue
            if self._are_dependencies_complete(task):
                ready.append(task)
        return ready

    def mark_complete(self, task_id: str) -> None:
        self._get_task(task_id).status = STATUS_COMPLETE

    def mark_running(self, task_id: str) -> None:
        task = self._get_task(task_id)
        if task.status != STATUS_PENDING:
            raise ValueError(f"Task '{task_id}' is not pending")
        task.status = STATUS_RUNNING

    def mark_failed(self, task_id: str) -> None:
        self._get_task(task_id).status = STATUS_FAILED

    def get_task(self, task_id: str) -> TaskNode:
        return self._get_task(task_id)

    def get_all_tasks(self) -> list[TaskNode]:
        return list(self._tasks.values())

    def has_unfinished_tasks(self) -> bool:
        return any(task.status in {STATUS_PENDING, STATUS_RUNNING} for task in self._tasks.values())

    def _get_task(self, task_id: str) -> TaskNode:
        try:
            return self._tasks[task_id]
        except KeyError as exc:
            raise ValueError(f"Task '{task_id}' not found") from exc

    def _are_dependencies_complete(self, task: TaskNode) -> bool:
        for dep_id in task.dependencies:
            dep = self._tasks.get(dep_id)
            if dep is None:
                raise ValueError(f"Task '{task.id}' depends on missing task '{dep_id}'")
            if dep.status != STATUS_COMPLETE:
                return False
        return True
