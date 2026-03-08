from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

import numpy as np
from PySide6.QtCore import QObject, QThread, QTimer, Signal, Slot

from jarvis.core.runtime import build_default_orchestrator

CONFIG_PATH = Path("config/gui_profile.json")


class RuntimeWorker(QObject):
    event_emitted = Signal(dict)

    def __init__(self) -> None:
        super().__init__()
        self._orchestrator = build_default_orchestrator()

    @Slot(str)
    def execute_command(self, command: str) -> None:
        clean = " ".join(command.strip().split())
        if not clean:
            return

        self.event_emitted.emit({"type": "task_started", "command": clean})
        self.event_emitted.emit({"type": "voice_phase", "phase": "thinking"})

        try:
            result = asyncio.run(self._orchestrator.handle_command(clean))
        except Exception as exc:  # pragma: no cover - runtime environment specific
            self.event_emitted.emit({"type": "task_failed", "command": clean, "error": str(exc)})
            self.event_emitted.emit({"type": "voice_phase", "phase": "idle"})
            return

        for event in result.get("execution_events", []):
            intent = event.get("intent") or "legacy_command"
            self.event_emitted.emit(
                {
                    "type": "agent_update",
                    "agent": self._agent_for_intent(intent),
                    "status": "running",
                    "task_id": str(event.get("task_id", "")),
                }
            )

        responses: list[str] = []
        for task_id, task_result in sorted(result.get("results", {}).items()):
            if task_result.get("status") in {"complete", "done"}:
                payload = task_result.get("result", {})
                text = payload.get("message") or payload.get("response") or "Done."
                responses.append(text)
                self.event_emitted.emit({"type": "task_completed", "task_id": task_id, "message": text})
            else:
                error = task_result.get("error", "Task failed.")
                responses.append(error)
                self.event_emitted.emit({"type": "task_failed", "task_id": task_id, "error": error})

        self.event_emitted.emit({"type": "response", "role": "assistant", "text": "\n".join(responses) or "Done."})

    @staticmethod
    def _agent_for_intent(intent: str) -> str:
        mapping = {
            "open_website": "BrowserAgent",
            "web_search": "ResearchAgent",
            "summarize_document": "ResearchAgent",
            "generate_code": "CodeAgent",
            "explain_code": "CodeAgent",
            "open_app": "SystemAgent",
            "create_timer": "ProductivityAgent",
            "start_focus_session": "ProductivityAgent",
        }
        return mapping.get(intent, "SystemAgent")


class EventBridge(QObject):
    event_emitted = Signal(dict)

    execute_command = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self._profile = self._load_profile()

        self._thread = QThread(self)
        self._worker = RuntimeWorker()
        self._worker.moveToThread(self._thread)
        self.execute_command.connect(self._worker.execute_command)
        self._worker.event_emitted.connect(self._forward_worker_event)
        self._thread.start()

        self._audio_timer = QTimer(self)
        self._audio_timer.timeout.connect(self._emit_audio_sample)
        self._audio_timer.start(45)

        self._status_timer = QTimer(self)
        self._status_timer.timeout.connect(self._emit_system_tick)
        self._status_timer.start(1200)

    def shutdown(self) -> None:
        self._audio_timer.stop()
        self._status_timer.stop()
        self._thread.quit()
        self._thread.wait(1500)

    @Slot(str)
    def send_command(self, text: str) -> None:
        clean = " ".join(text.strip().split())
        if not clean:
            return
        self.event_emitted.emit({"type": "response", "role": "user", "text": clean})
        self.event_emitted.emit({"type": "voice_phase", "phase": "thinking"})
        self.execute_command.emit(clean)

    @Slot()
    def interrupt_tts(self) -> None:
        self.event_emitted.emit({"type": "tts_interrupted"})
        self.event_emitted.emit({"type": "voice_phase", "phase": "idle"})

    @Slot(dict)
    def apply_profile(self, profile: dict[str, Any]) -> None:
        self._profile = {**self._profile, **profile}
        self._save_profile(self._profile)
        self.event_emitted.emit({"type": "profile_updated", "profile": self._profile})

    @property
    def profile(self) -> dict[str, Any]:
        return dict(self._profile)

    @Slot(dict)
    def _forward_worker_event(self, payload: dict[str, Any]) -> None:
        event_type = payload.get("type")
        if event_type == "response":
            text = str(payload.get("text", ""))
            duration_ms = int(max(500, min(3200, len(text) * 28)))
            self.event_emitted.emit({"type": "tts_started"})
            self.event_emitted.emit({"type": "voice_phase", "phase": "speaking"})
            self.event_emitted.emit(payload)
            QTimer.singleShot(
                duration_ms,
                lambda: (
                    self.event_emitted.emit({"type": "tts_finished"}),
                    self.event_emitted.emit({"type": "voice_phase", "phase": "idle"}),
                ),
            )
            return

        if event_type == "agent_update":
            self.event_emitted.emit(payload)
            self.event_emitted.emit({"type": "voice_phase", "phase": "planning"})
            self.event_emitted.emit(
                {
                    "type": "analytics",
                    "stats": {"agent_activity": payload.get("agent", "SystemAgent")},
                }
            )
            return

        self.event_emitted.emit(payload)

    def _emit_audio_sample(self) -> None:
        # The GUI can be wired to actual microphone/TTS streams later;
        # this keeps visuals alive when no stream is connected.
        fft = np.abs(np.fft.rfft(np.random.normal(0.0, 1.0, size=128)))
        norm = fft / max(float(fft.max()), 1e-6)
        self.event_emitted.emit(
            {
                "type": "audio_frame",
                "amplitude": float(np.clip(norm.mean(), 0.0, 1.0)),
                "bands": norm[:24].tolist(),
            }
        )

    def _emit_system_tick(self) -> None:
        self.event_emitted.emit(
            {
                "type": "system_status",
                "status": "online",
                "model": "local",
            }
        )

    @staticmethod
    def _load_profile() -> dict[str, Any]:
        defaults: dict[str, Any] = {
            "voice": {"name": "Default", "pitch": 1.0, "speed": 1.0, "tone": "balanced"},
            "aliases": {"yt": "open youtube", "mail": "open gmail"},
            "macros": {
                "Start Work": ["open notion", "open slack", "start focus session"],
                "Morning Routine": ["open email", "open calendar", "read news"],
            },
            "appearance": {
                "theme": "nebula",
                "particle_density": 60000,
                "primary": "#00c8ff",
                "secondary": "#8b5cf6",
            },
            "personality": {"tone": "professional", "humor": 0.2, "verbosity": 0.5},
            "automation": [{"name": "Morning Routine", "enabled": True}],
        }

        if not CONFIG_PATH.exists():
            CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
            CONFIG_PATH.write_text(json.dumps(defaults, indent=2), encoding="utf-8")
            return defaults

        try:
            loaded = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            return {**defaults, **loaded}
        except Exception:
            return defaults

    @staticmethod
    def _save_profile(profile: dict[str, Any]) -> None:
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        CONFIG_PATH.write_text(json.dumps(profile, indent=2), encoding="utf-8")
