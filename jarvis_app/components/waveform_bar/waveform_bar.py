from __future__ import annotations

from collections import deque

import numpy as np
from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QWidget


class WaveformBar(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setMinimumHeight(120)
        self._amplitude = 0.0
        self._bands = [0.0] * 24
        self._history = deque([0.0] * 120, maxlen=120)

    def update_audio(self, amplitude: float, bands: list[float]) -> None:
        self._amplitude = float(np.clip(amplitude, 0.0, 1.0))
        if bands:
            self._bands = [float(np.clip(v, 0.0, 1.0)) for v in bands]
        self._history.append(self._amplitude)
        self.update()

    def paintEvent(self, _event) -> None:
        w = self.width()
        h = self.height()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor(8, 12, 28, 180))

        baseline = h * 0.7
        path = QPainterPath()
        path.moveTo(0, baseline)

        if len(self._history) > 1:
            step = w / (len(self._history) - 1)
            for i, amp in enumerate(self._history):
                y = baseline - (amp * h * 0.5)
                path.lineTo(i * step, y)

        pen = QPen(QColor("#38bdf8"))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawPath(path)

        bar_count = len(self._bands)
        if bar_count:
            slot_w = max(w / bar_count, 1.0)
            for i, band in enumerate(self._bands):
                x = i * slot_w
                bar_h = max(4.0, band * h * 0.55)
                color = QColor("#22d3ee")
                color.setAlpha(int(90 + 140 * band))
                painter.fillRect(int(x + 1), int(h - bar_h), int(slot_w - 2), int(bar_h), color)

        glow = QColor("#c084fc")
        glow.setAlpha(int(25 + 110 * self._amplitude))
        painter.setPen(Qt.NoPen)
        painter.setBrush(glow)
        painter.drawEllipse(QPointF(w * 0.5, h * 0.5), w * 0.18, h * (0.06 + self._amplitude * 0.16))
        painter.end()
