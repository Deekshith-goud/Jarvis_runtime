from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QSlider,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class SettingsView(QWidget):
    profile_changed = Signal(dict)

    def __init__(self, initial_profile: dict[str, Any] | None = None, parent=None) -> None:
        super().__init__(parent)
        self._profile = dict(initial_profile or {})

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)

        self.tabs = QTabWidget(self)
        root.addWidget(self.tabs)

        self.tabs.addTab(self._build_voices_tab(), "Voices")
        self.tabs.addTab(self._build_alias_tab(), "Aliases")
        self.tabs.addTab(self._build_macro_tab(), "Macros")
        self.tabs.addTab(self._build_appearance_tab(), "Appearance")
        self.tabs.addTab(self._build_personality_tab(), "Personality")
        self.tabs.addTab(self._build_automation_tab(), "Automation")

    def _build_voices_tab(self) -> QWidget:
        tab = QWidget()
        layout = QFormLayout(tab)

        self.voice_name = QComboBox()
        self.voice_name.addItems(["Default", "Nova", "Echo", "Alloy"])
        self.voice_pitch = QSlider()
        self.voice_pitch.setOrientation(Qt.Horizontal)
        self.voice_pitch.setRange(50, 200)
        self.voice_pitch.setValue(100)

        self.voice_speed = QSlider()
        self.voice_speed.setOrientation(Qt.Horizontal)
        self.voice_speed.setRange(50, 200)
        self.voice_speed.setValue(100)

        self.voice_tone = QComboBox()
        self.voice_tone.addItems(["balanced", "warm", "analytical", "friendly"])

        save = QPushButton("Apply Voice")
        save.clicked.connect(self._emit_profile)

        layout.addRow("Voice", self.voice_name)
        layout.addRow("Pitch", self.voice_pitch)
        layout.addRow("Speed", self.voice_speed)
        layout.addRow("Tone", self.voice_tone)
        layout.addRow(save)
        return tab

    def _build_alias_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.alias_input = QLineEdit()
        self.alias_input.setPlaceholderText("yt=open youtube")
        self.alias_list = QListWidget()

        add = QPushButton("Add Alias")
        add.clicked.connect(self._add_alias)

        layout.addWidget(QLabel("Command aliases"))
        layout.addWidget(self.alias_input)
        layout.addWidget(add)
        layout.addWidget(self.alias_list, 1)
        return tab

    def _build_macro_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.macro_name = QLineEdit()
        self.macro_name.setPlaceholderText("Start Work")
        self.macro_steps = QTextEdit()
        self.macro_steps.setPlaceholderText("open notion\nopen slack\nstart focus session")
        self.macro_list = QListWidget()

        save = QPushButton("Save Macro")
        save.clicked.connect(self._add_macro)

        layout.addWidget(QLabel("Macro name"))
        layout.addWidget(self.macro_name)
        layout.addWidget(QLabel("Steps"))
        layout.addWidget(self.macro_steps)
        layout.addWidget(save)
        layout.addWidget(self.macro_list, 1)
        return tab

    def _build_appearance_tab(self) -> QWidget:
        tab = QWidget()
        layout = QFormLayout(tab)

        self.theme = QComboBox()
        self.theme.addItems(["nebula", "aurora", "graphite"])
        self.density = QSlider()
        self.density.setOrientation(Qt.Horizontal)
        self.density.setRange(50000, 100000)
        self.density.setValue(60000)

        apply_button = QPushButton("Apply Appearance")
        apply_button.clicked.connect(self._emit_profile)

        layout.addRow("Theme", self.theme)
        layout.addRow("Particle Density", self.density)
        layout.addRow(apply_button)
        return tab

    def _build_personality_tab(self) -> QWidget:
        tab = QWidget()
        layout = QFormLayout(tab)

        self.tone = QComboBox()
        self.tone.addItems(["professional", "concise", "playful", "mentor"])

        self.humor = QSlider()
        self.humor.setOrientation(Qt.Horizontal)
        self.humor.setRange(0, 100)
        self.humor.setValue(20)

        self.verbosity = QSlider()
        self.verbosity.setOrientation(Qt.Horizontal)
        self.verbosity.setRange(0, 100)
        self.verbosity.setValue(50)

        apply_button = QPushButton("Apply Personality")
        apply_button.clicked.connect(self._emit_profile)

        layout.addRow("Response Tone", self.tone)
        layout.addRow("Humor", self.humor)
        layout.addRow("Verbosity", self.verbosity)
        layout.addRow(apply_button)
        return tab

    def _build_automation_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.automation_name = QLineEdit()
        self.automation_name.setPlaceholderText("Morning Routine")
        self.automation_steps = QTextEdit()
        self.automation_steps.setPlaceholderText("open email\nopen calendar\nread news")
        self.automation_list = QListWidget()

        save = QPushButton("Save Automation")
        save.clicked.connect(self._add_automation)

        layout.addWidget(self.automation_name)
        layout.addWidget(self.automation_steps)
        layout.addWidget(save)
        layout.addWidget(self.automation_list, 1)
        return tab

    def _add_alias(self) -> None:
        entry = self.alias_input.text().strip()
        if "=" not in entry:
            return
        self.alias_list.addItem(entry)
        self.alias_input.clear()
        self._emit_profile()

    def _add_macro(self) -> None:
        name = self.macro_name.text().strip()
        steps = [s.strip() for s in self.macro_steps.toPlainText().splitlines() if s.strip()]
        if not name or not steps:
            return
        self.macro_list.addItem(f"{name}: {', '.join(steps)}")
        self.macro_name.clear()
        self.macro_steps.clear()
        self._emit_profile()

    def _add_automation(self) -> None:
        name = self.automation_name.text().strip()
        steps = [s.strip() for s in self.automation_steps.toPlainText().splitlines() if s.strip()]
        if not name or not steps:
            return
        self.automation_list.addItem(f"{name}: {', '.join(steps)}")
        self.automation_name.clear()
        self.automation_steps.clear()
        self._emit_profile()

    def _emit_profile(self) -> None:
        aliases: dict[str, str] = {}
        for i in range(self.alias_list.count()):
            text = self.alias_list.item(i).text()
            if "=" in text:
                key, value = text.split("=", 1)
                aliases[key.strip()] = value.strip()

        macros: dict[str, list[str]] = {}
        for i in range(self.macro_list.count()):
            text = self.macro_list.item(i).text()
            if ":" in text:
                key, value = text.split(":", 1)
                macros[key.strip()] = [v.strip() for v in value.split(",") if v.strip()]

        automation: list[dict[str, Any]] = []
        for i in range(self.automation_list.count()):
            text = self.automation_list.item(i).text()
            if ":" in text:
                key, value = text.split(":", 1)
                automation.append(
                    {
                        "name": key.strip(),
                        "enabled": True,
                        "steps": [v.strip() for v in value.split(",") if v.strip()],
                    }
                )

        self._profile = {
            **self._profile,
            "voice": {
                "name": self.voice_name.currentText(),
                "pitch": self.voice_pitch.value() / 100.0,
                "speed": self.voice_speed.value() / 100.0,
                "tone": self.voice_tone.currentText(),
            },
            "aliases": aliases,
            "macros": macros,
            "appearance": {
                "theme": self.theme.currentText(),
                "particle_density": int(self.density.value()),
            },
            "personality": {
                "tone": self.tone.currentText(),
                "humor": self.humor.value() / 100.0,
                "verbosity": self.verbosity.value() / 100.0,
            },
            "automation": automation,
        }
        self.profile_changed.emit(dict(self._profile))

    def hydrate(self, profile: dict[str, Any]) -> None:
        if not profile:
            return
        self._profile = dict(profile)
