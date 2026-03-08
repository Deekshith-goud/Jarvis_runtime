from __future__ import annotations

import math

import numpy as np
from PySide6.QtCore import QPointF
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QWidget


class WaveformRenderer(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setMinimumHeight(112)
        self._amp = 0.0
        self._bands = [0.0] * 24
        self._time = 0.0

    def update_audio(self, amplitude: float, bands: list[float]) -> None:
        self._amp = float(np.clip(amplitude, 0.0, 1.0))
        if bands:
            self._bands = [float(np.clip(v, 0.0, 1.0)) for v in bands]
        self._time += 0.11
        self.update()

    def paintEvent(self, _event) -> None:
        w = max(self.width(), 1)
        h = max(self.height(), 1)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.fillRect(self.rect(), QColor(7, 11, 25, 150))

        center = h * 0.58
        samples = 220
        base_amp = (h * 0.22) * (0.2 + self._amp)

        path = QPainterPath()
        path.moveTo(0.0, center)
        for i in range(samples):
            x = (i / (samples - 1)) * w
            b = self._bands[i % len(self._bands)] if self._bands else 0.0
            y = center + math.sin((x / 32.0) + self._time * 3.8) * base_amp * (0.45 + b)
            y += math.sin((x / 75.0) - self._time * 2.1) * base_amp * 0.35
            path.lineTo(x, y)

        glow_pen = QPen(QColor(56, 189, 248, int(110 + self._amp * 90)))
        glow_pen.setWidth(7)
        painter.setPen(glow_pen)
        painter.drawPath(path)

        main_pen = QPen(QColor("#22d3ee"))
        main_pen.setWidth(2)
        painter.setPen(main_pen)
        painter.drawPath(path)

        pulse = QColor("#f472b6")
        pulse.setAlpha(int(20 + self._amp * 120))
        painter.setPen(QPen(pulse, 1))
        painter.drawEllipse(QPointF(w * 0.5, center), w * (0.08 + self._amp * 0.06), h * 0.16)
        painter.end()
