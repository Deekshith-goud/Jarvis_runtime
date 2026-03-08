import asyncio

from jarvis.core.agent_registry import AgentRegistry
from jarvis.core.context import ContextInjector
from jarvis.core.task_graph import TaskGraph, TaskNode
from jarvis.execution.executor import Executor
from jarvis.memory.memory_system import JarvisMemory, LongTermMemory, SessionMemory, ShortTermMemory


class ContextAwareAgent:
    capabilities = ["open_youtube"]

    async def execute(self, task, context):
        # Agent can read/write memory from injected context.
        short_term = context["memory"]["short_term"]
        short_term.set_current_command({"intent": task["intent"]})
        context["session"]["last_intent"] = task["intent"]
        return {
            "has_memory": "memory" in context,
            "has_config": "config" in context,
            "has_system_state": "system_state" in context,
        }


def test_executor_injects_default_context(isolated_cwd):
    memory = JarvisMemory(
        short_term=ShortTermMemory(),
        session=SessionMemory(),
        long_term=LongTermMemory(db_path=isolated_cwd / "ctx_memory.db"),
    )
    injector = ContextInjector(
        memory_manager=memory,
        runtime_config={"environment": "test"},
        session_state={"session_id": "s-1"},
        system_state_provider=lambda: {"mode": "active"},
    )

    registry = AgentRegistry()
    registry.register(ContextAwareAgent())
    executor = Executor(registry, context_injector=injector)

    graph = TaskGraph()
    graph.add_task(TaskNode(id="task1", intent="open_youtube"))
    results = asyncio.run(executor.execute(graph))

    assert results["task1"]["status"] == "complete"
    output = results["task1"]["result"]
    assert output["has_memory"] is True
    assert output["has_config"] is True
    assert output["has_system_state"] is True
    assert memory.short_term.get_current_command()["intent"] == "open_youtube"


def test_executor_preserves_override_context_values():
    registry = AgentRegistry()
    registry.register(ContextAwareAgent())
    executor = Executor(registry)

    graph = TaskGraph()
    graph.add_task(TaskNode(id="task1", intent="open_youtube"))
    custom_context = {"config": {"mode": "custom"}, "session": {"session_id": "override"}}
    results = asyncio.run(executor.execute(graph, context=custom_context))

    assert results["task1"]["status"] == "complete"
