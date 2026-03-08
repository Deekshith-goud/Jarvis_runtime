from __future__ import annotations

from typing import Any, Callable

from jarvis.memory.memory_system import JarvisMemory


class ContextInjector:
    def __init__(
        self,
        memory_manager: JarvisMemory | None = None,
        runtime_config: dict[str, Any] | None = None,
        session_state: dict[str, Any] | None = None,
        services: dict[str, Any] | None = None,
        system_state_provider: Callable[[], dict[str, Any]] | None = None,
    ) -> None:
        self.memory_manager = memory_manager or JarvisMemory()
        self.runtime_config = runtime_config or {}
        self.session_state = session_state or {}
        self.services = services or {}
        self.system_state_provider = system_state_provider or (lambda: {"mode": "normal", "healthy": True})

    def build(self, override: dict[str, Any] | None = None) -> dict[str, Any]:
        context = {} if override is None else override
        context.setdefault(
            "memory",
            {
                "short_term": self.memory_manager.short_term,
                "session": self.memory_manager.session,
                "long_term": self.memory_manager.long_term,
                "manager": self.memory_manager,
            },
        )
        context.setdefault("config", dict(self.runtime_config))
        context.setdefault("session", dict(self.session_state))
        context.setdefault("services", dict(self.services))
        context.setdefault("system_state", dict(self.system_state_provider()))
        return context
