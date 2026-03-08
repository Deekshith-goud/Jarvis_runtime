import asyncio
import json
import time

from jarvis.core.agent_registry import AgentRegistry
from jarvis.core.events import EventLogger
from jarvis.core.task_graph import STATUS_COMPLETE, STATUS_FAILED, TaskGraph, TaskNode
from jarvis.execution.executor import Executor


class BrowserAgent:
    capabilities = ["open_youtube", "search_web"]

    async def execute(self, task, context):
        await asyncio.sleep(0.2)
        return {"handled": task["intent"], "context": context}


class ProductivityAgent:
    capabilities = ["set_timer"]

    async def execute(self, task, context):
        await asyncio.sleep(0.2)
        return {"handled": task["intent"], "context": context}


class SequenceAgent:
    capabilities = ["task_a", "task_b"]

    async def execute(self, task, context):
        events = context.setdefault("events", [])
        events.append(task["id"])
        return {"ok": True}


def test_executor_runs_independent_tasks_in_parallel():
    registry = AgentRegistry()
    registry.register(BrowserAgent())
    registry.register(ProductivityAgent())
    executor = Executor(registry)

    graph = TaskGraph()
    graph.add_task(TaskNode(id="task1", intent="open_youtube"))
    graph.add_task(TaskNode(id="task2", intent="set_timer", params={"duration": 300}))

    start = time.perf_counter()
    results = asyncio.run(executor.execute(graph))
    elapsed = time.perf_counter() - start

    assert results["task1"]["status"] == "complete"
    assert results["task2"]["status"] == "complete"
    assert graph.get_task("task1").status == STATUS_COMPLETE
    assert graph.get_task("task2").status == STATUS_COMPLETE
    assert elapsed < 0.35


def test_executor_respects_dependencies():
    registry = AgentRegistry()
    registry.register(SequenceAgent())
    executor = Executor(registry)

    graph = TaskGraph()
    graph.add_task(TaskNode(id="task1", intent="task_a"))
    graph.add_task(TaskNode(id="task2", intent="task_b", dependencies=["task1"]))

    context = {}
    results = asyncio.run(executor.execute(graph, context=context))

    assert results["task1"]["status"] == "complete"
    assert results["task2"]["status"] == "complete"
    assert context["events"] == ["task1", "task2"]


def test_executor_marks_task_failed_if_no_agent_found():
    registry = AgentRegistry()
    executor = Executor(registry)

    graph = TaskGraph()
    graph.add_task(TaskNode(id="task1", intent="open_youtube"))

    results = asyncio.run(executor.execute(graph))

    assert results["task1"]["status"] == "failed"
    assert graph.get_task("task1").status == STATUS_FAILED


def test_executor_emits_required_events_to_jsonl(isolated_cwd):
    registry = AgentRegistry()
    registry.register(BrowserAgent())
    events_path = isolated_cwd / "events.jsonl"
    event_logger = EventLogger(storage="jsonl", path=events_path)
    executor = Executor(registry, event_logger=event_logger)

    graph = TaskGraph()
    graph.add_task(TaskNode(id="task1", intent="open_youtube"))
    asyncio.run(executor.execute(graph))

    lines = events_path.read_text(encoding="utf-8").strip().splitlines()
    events = [json.loads(line)["event"] for line in lines]

    assert "task_created" in events
    assert "agent_selected" in events
    assert "task_started" in events
    assert "task_completed" in events
