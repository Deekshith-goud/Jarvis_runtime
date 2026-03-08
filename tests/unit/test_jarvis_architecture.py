import asyncio
import time

from jarvis.agents.browser_agent import BrowserAgent
from jarvis.agents.productivity_agent import ProductivityAgent
from jarvis.core.agent import Agent
from jarvis.core.agent_registry import AgentRegistry
from jarvis.core.orchestrator import Orchestrator
from jarvis.core.planner import Planner
from jarvis.core.task_graph import TaskGraph, TaskNode
from jarvis.execution.executor import Executor


class SlowAgent(Agent):
    def __init__(self, name: str, intents: set[str]) -> None:
        self.name = name
        self.description = name
        self.capabilities = list(intents)
        self.intents = intents

    def can_handle(self, intent: str) -> bool:
        return intent in self.intents

    async def execute(self, task, context):
        await asyncio.sleep(0.2)
        return {"task_id": task["id"], "agent": self.name}


class SpyPlanner(Planner):
    def __init__(self):
        super().__init__()
        self.called = False

    def create_plan(self, parsed_command):
        self.called = True
        graph = TaskGraph()
        graph.add_task(TaskNode(id="task1", intent="open_youtube"))
        return graph


def test_planner_builds_parallel_task_graph_for_multi_command():
    planner = Planner()
    graph = planner.create_plan({"text": "open youtube and set timer 5 minutes"})

    all_tasks = graph.get_all_tasks()
    assert len(all_tasks) == 2
    assert graph.get_task("task1").intent == "open_youtube"
    assert graph.get_task("task2").intent == "set_timer"
    assert graph.get_task("task2").params["duration"] == 300
    assert graph.get_task("task1").dependencies == []
    assert graph.get_task("task2").dependencies == []


def test_engine_runs_independent_tasks_in_parallel():
    registry = AgentRegistry(
        [
            SlowAgent("browser_agent", {"open_youtube"}),
            SlowAgent("productivity_agent", {"set_timer"}),
        ]
    )
    engine = Executor(registry)
    graph = TaskGraph()
    graph.add_task(TaskNode(id="task1", intent="open_youtube"))
    graph.add_task(TaskNode(id="task2", intent="set_timer"))

    start = time.perf_counter()
    results = asyncio.run(engine.execute(graph))
    elapsed = time.perf_counter() - start

    assert results["task1"]["status"] == "complete"
    assert results["task2"]["status"] == "complete"
    assert elapsed < 0.35


def test_orchestrator_calls_create_plan_and_executor_flow():
    registry = AgentRegistry([BrowserAgent()])
    planner = SpyPlanner()
    executor = Executor(registry=registry)
    orchestrator = Orchestrator(planner=planner, agent_registry=registry, executor=executor)

    output = asyncio.run(orchestrator.orchestrate({"text": "open youtube", "segments": ["open youtube"]}))

    assert planner.called is True
    assert output["results"]["task1"]["status"] == "complete"
    assert output["summary"]["successful_tasks"] == 1


def test_orchestrator_is_plug_and_play_for_agents():
    registry = AgentRegistry([BrowserAgent(), ProductivityAgent()])
    planner = Planner()
    orchestrator = Orchestrator(planner=planner, agent_registry=registry)

    output = asyncio.run(
        orchestrator.orchestrate(
            {
                "text": "open youtube and set timer 5 minutes",
                "segments": ["open youtube", "set timer 5 minutes"],
                "source": "test",
            }
        )
    )

    assert output["results"]["task1"]["status"] == "complete"
    assert output["results"]["task2"]["status"] == "complete"
    assert output["summary"]["total_tasks"] == 2
    assert output["summary"]["failed_tasks"] == 0
    assert len(output["execution_events"]) >= 2
