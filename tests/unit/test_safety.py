import asyncio

from jarvis.core.agent_registry import AgentRegistry
from jarvis.core.safety import SafetyValidator
from jarvis.core.task_graph import STATUS_FAILED, TaskGraph, TaskNode
from jarvis.execution.executor import Executor


class SystemAgent:
    capabilities = ["open_app", "shutdown_system"]

    async def execute(self, task, context):
        return {"ok": True}


def test_safety_validator_blocks_dangerous_intent():
    validator = SafetyValidator()
    task = TaskNode(id="task1", intent="format_disk", params={})

    allowed, reason = validator.validate_task(task)

    assert allowed is False
    assert "Blocked dangerous intent" in reason


def test_safety_validator_detects_injection_in_params():
    validator = SafetyValidator()
    task = TaskNode(id="task1", intent="open_app", params={"target": "notepad.exe && rm -rf /"})

    allowed, reason = validator.validate_task(task)

    assert allowed is False
    assert "Potential command injection" in reason


def test_safety_validator_enforces_confirmation_for_shutdown():
    validator = SafetyValidator()
    blocked = TaskNode(id="task1", intent="shutdown_system", params={})
    allowed = TaskNode(id="task2", intent="shutdown_system", params={"confirmed": True})

    blocked_result, _ = validator.validate_task(blocked)
    allowed_result, _ = validator.validate_task(allowed)

    assert blocked_result is False
    assert allowed_result is True


def test_safety_validator_enforces_allowed_app_paths():
    validator = SafetyValidator(allowed_app_paths=[r"C:\Allowed"])
    unsafe = TaskNode(id="task1", intent="open_app", params={"target": r"C:\Temp\evil.exe"})
    safe = TaskNode(id="task2", intent="open_app", params={"target": r"C:\Allowed\tool.exe"})

    unsafe_result, _ = validator.validate_task(unsafe)
    safe_result, _ = validator.validate_task(safe)

    assert unsafe_result is False
    assert safe_result is True


def test_executor_blocks_unsafe_task_before_agent_execution():
    registry = AgentRegistry()
    registry.register(SystemAgent())
    executor = Executor(registry, safety_validator=SafetyValidator())

    graph = TaskGraph()
    graph.add_task(TaskNode(id="task1", intent="delete_system_files", params={}))

    result = asyncio.run(executor.execute(graph))

    assert result["task1"]["status"] == "failed"
    assert graph.get_task("task1").status == STATUS_FAILED
