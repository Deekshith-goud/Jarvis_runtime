from __future__ import annotations

import time

import numpy as np
from PySide6.QtCore import QTimer
from PySide6.QtGui import QMatrix4x4, QVector3D
from PySide6.QtOpenGLWidgets import QOpenGLWidget

from jarvis_app.rendering.gpu_renderer import GPUParticleRenderer
from jarvis_app.rendering.particle_engine import ParticleEngine


class NeuralSphereWidget(QOpenGLWidget):
    def __init__(self, particle_count: int = 70000, parent=None) -> None:
        super().__init__(parent)
        self.setMinimumSize(360, 360)

        self._engine = ParticleEngine(particle_count=particle_count)
        self._gpu = GPUParticleRenderer()

        self._phase = "idle"
        self._audio_level = 0.0
        self._last_ts = time.perf_counter()

        self._projection = QMatrix4x4()
        self._aspect = 1.0

        self._timer = QTimer(self)
        self._timer.timeout.connect(self.update)
        self._timer.start(16)

    def initializeGL(self) -> None:  # type: ignore[override]
        self._gpu.initialize()

    def resizeGL(self, w: int, h: int) -> None:  # type: ignore[override]
        self._aspect = max(float(w) / max(float(h), 1.0), 1e-3)
        self._projection.setToIdentity()
        self._projection.perspective(45.0, self._aspect, 0.1, 50.0)

    def set_phase(self, phase: str) -> None:
        self._phase = phase

    def set_audio_level(self, level: float) -> None:
        self._audio_level = float(np.clip(level, 0.0, 1.0))

    def set_density(self, density: int) -> None:
        self._engine.set_density(density)

    def set_agent_activity(self, agent: str, active: bool) -> None:
        self._engine.set_agent_activity(agent, active)

    def paintGL(self) -> None:  # type: ignore[override]
        now = time.perf_counter()
        dt = max(now - self._last_ts, 1.0 / 240.0)
        self._last_ts = now

        frame = self._engine.update(dt=dt, audio_level=self._audio_level, phase=self._phase)

        view = QMatrix4x4()
        cam_x, cam_y, cam_z = frame.camera_orbit
        view.lookAt(
            QVector3D(cam_x, cam_y, cam_z),
            QVector3D(0.0, 0.0, 0.0),
            QVector3D(0.0, 1.0, 0.0),
        )
        mvp = self._projection * view

        self._gpu.clear(self.width(), self.height())

        self._gpu.render_points(frame.deep_space, mvp, additive=False)
        self._gpu.render_points(frame.background, mvp, additive=False)

        self._gpu.render_lines(frame.neural_lines, mvp, additive=False, width=1.0)
        self._gpu.render_points(frame.neural_points, mvp, additive=True)

        self._gpu.render_points(frame.core_trails, mvp, additive=True)
        self._gpu.render_points(frame.core_glow, mvp, additive=True)
        self._gpu.render_points(frame.core_points, mvp, additive=True)
        self._gpu.render_lines(frame.core_lines, mvp, additive=True, width=1.6)
