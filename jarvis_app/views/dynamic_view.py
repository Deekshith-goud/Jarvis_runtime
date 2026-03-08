from __future__ import annotations

import math
from typing import Any

from PySide6.QtCore import QDateTime, QPropertyAnimation, QRect, Qt, QTimer, Signal, QEasingCurve, QPoint
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from jarvis_app.components.neural_sphere.neural_sphere_widget import NeuralSphereWidget
from jarvis_app.components.task_graph.task_graph import TaskGraphWidget
from jarvis_app.components.agent_monitor.agent_monitor import AgentMonitorWidget


class FloatingAgentLabel(QLabel):
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            background-color: rgba(34, 211, 238, 40);
            color: #22d3ee;
            border: 1px solid #22d3ee;
            border-radius: 12px;
            padding: 4px 10px;
            font-weight: bold;
        """)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.hide()


class RadialButton(QPushButton):
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setFixedSize(90, 40)
        self.setStyleSheet("""
            QPushButton {
                background-color: rgba(15, 23, 42, 210);
                color: #e2e8f0;
                border: 1px solid #334155;
                border-radius: 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                border-color: #22d3ee;
                background-color: rgba(30, 41, 59, 230);
            }
        """)


class DynamicView(QWidget):
    command_submitted = Signal(str)
    file_dropped = Signal(str)
    stop_audio = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setAcceptDrops(True)
        # We will use absolute positioning for overlays
        
        # 1. Base components
        self.sphere = NeuralSphereWidget(particle_count=60000, parent=self)
        
        # 2. Idle Elements
        self.clock = QLabel("--:--", self)
        self.clock.setAlignment(Qt.AlignCenter)
        self.clock.setObjectName("clockLabel")
        
        self.hint = QLabel('Say "Jarvis", click sphere, or hold to talk.', self)
        self.hint.setAlignment(Qt.AlignCenter)
        self.hint.setObjectName("hintLabel")
        
        self.status = QLabel("Idle", self)
        self.status.setAlignment(Qt.AlignCenter)
        self.status.setObjectName("statusLabel")
        
        # Timer for clock
        self._clock_timer = QTimer(self)
        self._clock_timer.timeout.connect(self._update_clock)
        self._clock_timer.start(1000)
        self._update_clock()
        
        # 3. Dynamic Overlays
        
        # 3.1 Task Graph (Hidden by default)
        self.task_graph = TaskGraphWidget(self)
        self.task_graph.hide()
        self.task_graph.setStyleSheet("background: transparent;")
        
        # 3.1.1 Agent Monitor (Hidden by default, used as a temporary tool panel later)
        self.agent_monitor = AgentMonitorWidget(self)
        self.agent_monitor.hide()
        
        # 3.2 Command Input Overlay (Hidden by default)
        self.command_input_container = QFrame(self)
        self.command_input_container.setObjectName("commandInputContainer")
        self.command_input_container.setStyleSheet("""
            QFrame#commandInputContainer {
                background-color: rgba(15, 23, 42, 210);
                border: 1px solid #334155;
                border-radius: 12px;
            }
        """)
        input_layout = QVBoxLayout(self.command_input_container)
        input_layout.setContentsMargins(10, 10, 10, 10)
        
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("Type command...")
        self.command_input.returnPressed.connect(self._on_submit)
        self.command_input.setStyleSheet("background: transparent; border: none;")
        
        input_layout.addWidget(self.command_input)
        self.command_input_container.hide()
        
        # 3.3 Radial Menu
        self.radial_buttons: list[RadialButton] = []
        self.radial_options = ["System", "Browser", "Research", "Code", "Media", "Productivity", "Memory"]
        self.menus_visible = False
        
        for option in self.radial_options:
            btn = RadialButton(option, self)
            btn.hide()
            btn.clicked.connect(lambda checked=False, opt=option: self._on_radial_option_clicked(opt))
            self.radial_buttons.append(btn)
            
        self._radial_animations: list[QPropertyAnimation] = []
        
        # 3.4 Temporary Tool Panel Container
        self.tool_panel_container = QFrame(self)
        self.tool_panel_container.setObjectName("toolPanelContainer")
        self.tool_panel_container.setStyleSheet("""
            QFrame#toolPanelContainer {
                background-color: rgba(15, 23, 42, 230);
                border: 1px solid #1e293b;
                border-radius: 12px;
            }
        """)
        self.tool_panel_layout = QVBoxLayout(self.tool_panel_container)
        self.tool_panel_layout.setContentsMargins(10, 10, 10, 10)
        self.tool_panel_label = QLabel("Tool Panel", self.tool_panel_container)
        self.tool_panel_label.setStyleSheet("font-weight: bold; font-size: 16px; color: #93c5fd; background: transparent;")
        self.tool_panel_layout.addWidget(self.tool_panel_label)
        self.tool_panel_content = QVBoxLayout()
        self.tool_panel_layout.addLayout(self.tool_panel_content)
        self.tool_panel_container.hide()
        
        # Voice input tracking
        self._sphere_press_timer = QTimer(self)
        self._sphere_press_timer.setSingleShot(True)
        self._sphere_press_timer.timeout.connect(self._on_sphere_held)
        self._is_voice_active = False
        
        # Agent connection lines tracking
        self._active_agents: dict[str, FloatingAgentLabel] = {}

        # Wiring sphere events
        self.sphere.installEventFilter(self)

    def _update_clock(self) -> None:
        self.clock.setText(QDateTime.currentDateTime().toString("hh:mm:ss AP"))

    def set_status(self, text: str) -> None:
        self.status.setText(text)

    def set_hint(self, text: str) -> None:
        self.hint.setText(text)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        w = self.width()
        h = self.height()
        
        # Center the sphere
        sphere_size = min(w, h) * 0.8
        self.sphere.setGeometry(int((w - sphere_size) / 2), int((h - sphere_size) / 2), int(sphere_size), int(sphere_size))
        
        # Position idle elements
        self.clock.setGeometry(0, 40, w, 50)
        self.status.setGeometry(0, 90, w, 30)
        self.hint.setGeometry(0, h - 80, w, 30)
        
        # Position command input (bottom center)
        input_w = 400
        input_h = 50
        self.command_input_container.setGeometry(int((w - input_w) / 2), h - 150, input_w, input_h)
        
        # Position task graph (top right)
        self.task_graph.setGeometry(w - 320, 40, 300, 200)
        
        # Position tool panel (left center)
        self.tool_panel_container.setGeometry(40, int(h / 2 - 200), 280, 400)
        
        # Update radial menu positions if visible
        if self.menus_visible:
            self._layout_radial_menu()

    def _layout_radial_menu(self) -> None:
        w = self.width()
        h = self.height()
        center_x = w / 2
        center_y = h / 2
        radius = min(w, h) * 0.45  # Slightly outside the sphere
        
        angle_step = 2 * math.pi / len(self.radial_buttons)
        start_angle = -math.pi / 2 # Start at top
        
        for i, btn in enumerate(self.radial_buttons):
            angle = start_angle + i * angle_step
            btn_x = center_x + radius * math.cos(angle) - btn.width() / 2
            btn_y = center_y + radius * math.sin(angle) - btn.height() / 2
            btn.move(int(btn_x), int(btn_y))

    def _toggle_radial_menu(self) -> None:
        self.menus_visible = not self.menus_visible
        
        self._radial_animations.clear()
        
        w = self.width()
        h = self.height()
        center_x = w / 2
        center_y = h / 2
        radius = min(w, h) * 0.45
        
        angle_step = 2 * math.pi / len(self.radial_buttons)
        start_angle = -math.pi / 2
        
        for i, btn in enumerate(self.radial_buttons):
            if self.menus_visible:
                btn.show()
                
                angle = start_angle + i * angle_step
                end_x = center_x + radius * math.cos(angle) - btn.width() / 2
                end_y = center_y + radius * math.sin(angle) - btn.height() / 2
                
                anim = QPropertyAnimation(btn, b"pos")
                anim.setDuration(300 + i * 50)
                anim.setStartValue(btn.pos())
                anim.setEndValue(btn.parent().mapFromGlobal(btn.parent().mapToGlobal(btn.pos())))
                anim.setStartValue(btn.pos() if btn.isVisible() else self.sphere.geometry().center())
                anim.setEndValue(btn.parent().mapFromParent(btn.parent().mapToParent(btn.pos()))) # Reset
                anim.setStartValue(self.sphere.geometry().center() - btn.rect().center())
                anim.setEndValue(self.sphere.geometry().center() - btn.rect().center())
                
                # Manual animation calculation for correct PyQt Point conversion issues
                anim = QPropertyAnimation(btn, b"geometry")
                anim.setDuration(400)
                anim.setEasingCurve(QEasingCurve.OutBack)
                start_rect = QRect(int(center_x - btn.width() / 2), int(center_y - btn.height() / 2), btn.width(), btn.height())
                end_rect = QRect(int(end_x), int(end_y), btn.width(), btn.height())
                
                anim.setStartValue(start_rect)
                anim.setEndValue(end_rect)
                self._radial_animations.append(anim)
                anim.start()
            else:
                anim = QPropertyAnimation(btn, b"geometry")
                anim.setDuration(300)
                anim.setEasingCurve(QEasingCurve.InBack)
                
                start_rect = btn.geometry()
                end_rect = QRect(int(center_x - btn.width() / 2), int(center_y - btn.height() / 2), btn.width(), btn.height())
                
                anim.setStartValue(start_rect)
                anim.setEndValue(end_rect)
                anim.finished.connect(btn.hide)
                self._radial_animations.append(anim)
                anim.start()

    def _on_radial_option_clicked(self, option: str) -> None:
        # Hide menus
        self._toggle_radial_menu()
        
        # Open appropriate tool panel
        self.tool_panel_label.setText(option)
        
        # Clear current content in tool panel
        while self.tool_panel_content.count():
            item = self.tool_panel_content.takeAt(0)
            if item.widget():
                item.widget().hide()
                
        # Populate based on option
        if option == "System":
            self.agent_monitor.show()
            self.tool_panel_content.addWidget(self.agent_monitor)
        # We can add other widgets here for other options
        
        self.tool_panel_container.show()
        
        # Example: auto-hide panel after 10 seconds of no interaction
        # We'll also hide it when a task completes
        QTimer.singleShot(10000, self.tool_panel_container.hide)

    # Drag & Drop Support
    def dragEnterEvent(self, event) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.sphere.set_phase("thinking") # Visual feedback
        else:
            event.ignore()

    def dragLeaveEvent(self, event) -> None:
        self.sphere.set_phase("idle")

    def dropEvent(self, event) -> None:
        self.sphere.set_phase("idle")
        for url in event.mimeData().urls():
            if url.isLocalFile():
                self.file_dropped.emit(url.toLocalFile())
        event.acceptProposedAction()

    # Event Filter for Sphere Interactions
    def eventFilter(self, obj, event) -> bool:
        if obj is self.sphere:
            if event.type() == event.Type.MouseButtonPress:
                if event.button() == Qt.LeftButton:
                    self._sphere_press_timer.start(500) # 500ms for "hold"
                    return True
                elif event.button() == Qt.RightButton:
                    self._toggle_radial_menu()
                    return True
            elif event.type() == event.Type.MouseButtonRelease:
                if event.button() == Qt.LeftButton:
                    if self._sphere_press_timer.isActive():
                        self._sphere_press_timer.stop()
                        self._on_sphere_clicked()
                    elif self._is_voice_active:
                        self._on_sphere_released()
                    return True
        return super().eventFilter(obj, event)

    def _on_sphere_clicked(self) -> None:
        if self.command_input_container.isHidden():
            self.command_input_container.show()
            self.command_input.setFocus()
            # If tool panel is open, hide it
            self.tool_panel_container.hide()
        else:
            self.command_input_container.hide()

    def _on_sphere_held(self) -> None:
        self._is_voice_active = True
        self.sphere.set_phase("listening")
        # In a real integration, we'd emit a signal to start voice recording here
        # E.g., self.start_voice.emit()

    def _on_sphere_released(self) -> None:
        self._is_voice_active = False
        self.sphere.set_phase("idle")
        # In a real integration, we'd emit a signal to stop voice recording here
        # E.g., self.stop_voice.emit()

    def _on_submit(self) -> None:
        text = self.command_input.text().strip()
        if not text:
            return
            
        if text.lower() in ("stop", "shut up"):
            self.stop_audio.emit()
            self.command_input.clear()
            self.command_input_container.hide()
            return
            
        self.command_submitted.emit(text)
        self.command_input.clear()
        self.command_input_container.hide()

    def update_audio(self, amp: float, bands: list[float]) -> None:
        self.sphere.set_audio_level(amp)

    def set_phase(self, phase: str) -> None:
        self.sphere.set_phase(phase)

    def set_agent_activity(self, agent: str, active: bool) -> None:
        self.sphere.set_agent_activity(agent, active)
        
        if active:
            if agent not in self._active_agents:
                label = FloatingAgentLabel(agent, self)
                label.show()
                # Position randomly around the sphere
                angle = len(self._active_agents) * (math.pi / 2.5) # Spread them out
                radius = min(self.width(), self.height()) * 0.4
                center_x = self.width() / 2
                center_y = self.height() / 2
                
                x = int(center_x + radius * math.cos(angle) - label.width() / 2)
                y = int(center_y + radius * math.sin(angle) - label.height() / 2)
                label.move(x, y)
                
                self._active_agents[agent] = label
                self.update() # Trigger paintEvent for lines
        else:
            if agent in self._active_agents:
                label = self._active_agents.pop(agent)
                label.hide()
                label.deleteLater()
                self.update()

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        
        if not self._active_agents:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        pen = QPen(QColor(34, 211, 238, 150)) # cyan with alpha
        pen.setWidth(2)
        pen.setStyle(Qt.DashLine)
        painter.setPen(pen)
        
        # Animate the dash offset based on time
        dash_offset = (QDateTime.currentMSecsSinceEpoch() / 20.0) % 20
        pen.setDashOffset(dash_offset)
        painter.setPen(pen)
        
        center_x = int(self.width() / 2)
        center_y = int(self.height() / 2)
        
        for label in self._active_agents.values():
            label_center = label.geometry().center()
            painter.drawLine(center_x, center_y, label_center.x(), label_center.y())
            
        # Schedule next update for animation
        QTimer.singleShot(30, self.update)
