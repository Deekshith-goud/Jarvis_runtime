from __future__ import annotations

from typing import Any

from PySide6.QtCore import QPropertyAnimation, Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from jarvis_app.event_bridge import EventBridge
from jarvis_app.state_manager import AppStateManager, UIState
from jarvis_app.views.dynamic_view import DynamicView
from jarvis_app.views.settings_view import SettingsView


class MainWindow(QMainWindow):
    def __init__(self, bridge: EventBridge, state_manager: AppStateManager) -> None:
        super().__init__()
        self.bridge = bridge
        self.state_manager = state_manager

        self.setWindowTitle("Jarvis Native Interface")
        self.resize(1460, 900)

        self.dynamic_view = DynamicView()
        
        # We might need settings accessible somehow, 
        # but for now we put it in a hidden container or rely on the radial menu.
        # Let's just set the dynamic view as central for now.
        
        shell = QWidget()
        shell_layout = QVBoxLayout(shell)
        shell_layout.setContentsMargins(0, 0, 0, 0)
        shell_layout.setSpacing(0)
        
        shell_layout.addWidget(self.dynamic_view)
        
        self.setCentralWidget(shell)

        self._apply_style()

        # Connect signals
        self.dynamic_view.command_submitted.connect(self._send_command)
        self.dynamic_view.file_dropped.connect(self._on_file_drop)
        self.dynamic_view.stop_audio.connect(self._stop_audio)

        self.bridge.event_emitted.connect(self._handle_event)
        
        # State manager might be less relevant now, but keeping for compatibility
        self.state_manager.state_changed.connect(self._on_state_changed)

        self._voice_phase = "ambient"
        self._on_state_changed(UIState.AMBIENT.value)
        self._apply_profile(self.bridge.profile)

    def closeEvent(self, event) -> None:  # type: ignore[override]
        self.bridge.shutdown()
        super().closeEvent(event)

    def _apply_style(self) -> None:
        self.setStyleSheet(
            """
            QMainWindow, QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #050816, stop:0.6 #080d24, stop:1 #120920);
                color: #e2e8f0;
                font-family: 'Segoe UI', 'Noto Sans';
            }
            QLineEdit {
                background-color: rgba(15, 23, 42, 190);
                border: 1px solid #1e293b;
                border-radius: 10px;
                padding: 10px;
                font-size: 16px;
            }
            QPushButton {
                background: #0f172a;
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 6px 10px;
            }
            QPushButton:hover {
                border-color: #22d3ee;
            }
            QLabel#clockLabel { font-size: 42px; font-weight: 600; color: #67e8f9; background: transparent; }
            QLabel#statusLabel { font-size: 20px; color: #cbd5e1; background: transparent; }
            QLabel#hintLabel { font-size: 15px; color: #94a3b8; background: transparent; }
            QLabel#voicePhaseLabel { font-size: 28px; font-weight: 600; color: #93c5fd; background: transparent; }
            """
        )

    def _send_command(self, text: str) -> None:
        self.bridge.send_command(text)

    def _stop_audio(self) -> None:
        self.bridge.send_command("stop")

    def _on_file_drop(self, path: str) -> None:
        # Generate a command to process the file
        self.bridge.send_command(f"read file {path}")

    def _apply_profile(self, profile: dict[str, Any]) -> None:
        appearance = profile.get("appearance", {})
        density = int(appearance.get("particle_density", 60000))
        self.dynamic_view.sphere.set_density(density)

    def _on_state_changed(self, value: str) -> None:
        pass # UIState handling is now mostly internal to dynamic_view

    def _handle_event(self, event: dict[str, Any]) -> None:
        event_type = event.get("type")

        if event_type == "audio_frame":
            amp = float(event.get("amplitude", 0.0))
            bands = event.get("bands", [])
            self.dynamic_view.update_audio(amp, bands)
            
            if self._voice_phase not in {"thinking", "speaking"} and amp > 0.18:
                self.dynamic_view.set_phase("listening")
                self._voice_phase = "listening"
            return

        if event_type == "voice_phase":
            phase = str(event.get("phase", "idle"))
            self.dynamic_view.set_phase(phase)
            self._voice_phase = phase
            return

        if event_type == "response":
            role = str(event.get("role", "assistant"))
            text = str(event.get("text", ""))
            # Text responses could be shown in a temporary subtitle overlay, but for now we rely on TTS
            return

        if event_type == "tts_started":
            self.dynamic_view.set_phase("speaking")
            self._voice_phase = "speaking"
            return

        if event_type == "tts_finished":
            self.dynamic_view.set_phase("listening")
            self._voice_phase = "listening"
            return

        if event_type == "task_started":
            command = str(event.get("command", ""))
            # Show task graph
            self.dynamic_view.task_graph.show()
            self.dynamic_view.task_graph.upsert_task(command, "running")
            self.dynamic_view.set_phase("thinking")
            return

        if event_type == "task_completed":
            task_id = str(event.get("task_id", "task"))
            self.dynamic_view.task_graph.upsert_task(task_id, "complete")
            # We could add a timer to hide the task graph after a few seconds
            QTimer.singleShot(3000, self._check_hide_task_graph)
            return

        if event_type in {"task_failed", "tts_interrupted"}:
            task_id = str(event.get("task_id", "task"))
            self.dynamic_view.task_graph.upsert_task(task_id, "failed")
            QTimer.singleShot(4000, self._check_hide_task_graph)
            return

        if event_type == "agent_update":
            agent = str(event.get("agent", "SystemAgent"))
            status = str(event.get("status", "running"))
            self.dynamic_view.set_agent_activity(agent, status == "running")
            # Optionally show connections to agent labels
            return

        if event_type == "analytics":
            # Analytics are no longer persistently displayed
            return

        if event_type == "system_status":
            self.dynamic_view.set_status(str(event.get("status", "Idle")).capitalize())
            return

        if event_type == "profile_updated":
            # Profile updates applied
            return
            
    def _check_hide_task_graph(self) -> None:
        # In a real app we'd check if all tasks are complete
        # For now we'll just hide it if there's no active task in the graph logic
        has_running = any(n.status == "running" for n in self.dynamic_view.task_graph._nodes)
        if not has_running:
            self.dynamic_view.task_graph.hide()
            self.dynamic_view.task_graph._nodes.clear() # Clear nodes when hiding

