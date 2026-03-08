from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QPointF, Qt, QTimer
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget


@dataclass
class TaskNode:
    task_id: str
    status: str
    phase: float = 0.0


class TaskGraphWidget(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._nodes: list[TaskNode] = []
        self._anim_timer = QTimer(self)
        self._anim_timer.timeout.connect(self._tick)
        self._anim_timer.start(40)

    def upsert_task(self, task_id: str, status: str) -> None:
        for node in self._nodes:
            if node.task_id == task_id:
                node.status = status
                self.update()
                return
        self._nodes.append(TaskNode(task_id=task_id, status=status))
        self.update()

    def _tick(self) -> None:
        moving = False
        for node in self._nodes:
            if node.status == "running":
                node.phase = (node.phase + 0.2) % 6.28
                moving = True
        if moving:
            self.update()

    def paintEvent(self, _event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor(6, 10, 22))

        if not self._nodes:
            painter.setPen(QColor("#64748b"))
            painter.drawText(self.rect(), Qt.AlignCenter, "Task graph is idle")
            painter.end()
            return

        w = self.width()
        h = self.height()
        slot_h = h / max(len(self._nodes), 1)

        for i, node in enumerate(self._nodes):
            y = (i + 0.5) * slot_h
            left = QPointF(w * 0.15, y)
            right = QPointF(w * 0.8, y)

            line_pen = QPen(QColor("#334155"))
            line_pen.setWidth(2)
            painter.setPen(line_pen)
            painter.drawLine(left, right)

            color = {
                "running": QColor("#22d3ee"),
                "complete": QColor("#34d399"),
                "failed": QColor("#fb7185"),
                "pending": QColor("#fbbf24"),
            }.get(node.status, QColor("#64748b"))
            if node.status == "running":
                pulse = (node.phase % 6.28) / 6.28
                color.setAlpha(int(110 + 120 * abs(0.5 - pulse) * 2))

            painter.setBrush(color)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(left, 8, 8)
            painter.drawEllipse(right, 8, 8)

            painter.setPen(QColor("#e2e8f0"))
            painter.drawText(int(w * 0.22), int(y + 4), f"{node.task_id} - {node.status}")

        painter.end()
