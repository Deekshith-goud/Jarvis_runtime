from __future__ import annotations

from jarvis.agents.browser_agent import BrowserAgent
from jarvis.agents.code_agent import CodeAgent
from jarvis.agents.legacy_command_agent import LegacyCommandAgent
from jarvis.agents.media_agent import MediaAgent
from jarvis.agents.productivity_agent import ProductivityAgent
from jarvis.agents.research_agent import ResearchAgent
from jarvis.agents.system_agent import SystemAgent
from jarvis.core.agent_registry import AgentRegistry
from jarvis.core.context import ContextInjector
from jarvis.core.orchestrator import Orchestrator
from jarvis.core.planner import Planner
from jarvis.execution.executor import Executor
from scheduler.timer_manager import TimerManager
from storage.database import DatabaseManager


def build_default_orchestrator() -> Orchestrator:
    database = DatabaseManager()
    timer_manager = TimerManager()

    def _timer_callback() -> None:
        print("[TIMER] Timer finished.")

    registry = AgentRegistry(
        agents=[
            SystemAgent(),
            BrowserAgent(),
            ProductivityAgent(),
            MediaAgent(),
            ResearchAgent(),
            CodeAgent(),
            LegacyCommandAgent(),
        ]
    )
    planner = Planner()
    context_injector = ContextInjector(
        services={
            "database": database,
            "timer_manager": timer_manager,
            "timer_callback": _timer_callback,
        }
    )
    executor = Executor(registry=registry, context_injector=context_injector)
    return Orchestrator(planner=planner, agent_registry=registry, executor=executor)
