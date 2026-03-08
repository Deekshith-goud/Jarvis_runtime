from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from PySide6.QtCore import QObject, Signal


class UIState(str, Enum):
    AMBIENT = "ambient"
    CONTROL_CENTER = "control_center"
    VOICE = "voice"
    COMMAND = "command"
    MINIMIZED = "minimized"
    SETTINGS = "settings"


@dataclass
class UIContext:
    status_text: str = "Idle"
    hint_text: str = "Say Jarvis"
    voice_phase: str = "idle"
    analytics: dict[str, Any] = field(default_factory=dict)


class AppStateManager(QObject):
    state_changed = Signal(str)
    context_changed = Signal(dict)

    def __init__(self) -> None:
        super().__init__()
        self._state = UIState.AMBIENT
        self._context = UIContext()

    @property
    def state(self) -> UIState:
        return self._state

    @property
    def context(self) -> UIContext:
        return self._context

    def set_state(self, state: UIState) -> None:
        if state == self._state:
            return
        self._state = state
        self.state_changed.emit(state.value)

    def update_context(self, **kwargs: Any) -> None:
        changed = False
        for key, value in kwargs.items():
            if hasattr(self._context, key) and getattr(self._context, key) != value:
                setattr(self._context, key, value)
                changed = True
        if changed:
            self.context_changed.emit(self.context_dict())

    def context_dict(self) -> dict[str, Any]:
        return {
            "status_text": self._context.status_text,
            "hint_text": self._context.hint_text,
            "voice_phase": self._context.voice_phase,
            "analytics": dict(self._context.analytics),
        }
