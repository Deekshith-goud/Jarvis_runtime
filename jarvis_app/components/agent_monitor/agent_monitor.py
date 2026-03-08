from __future__ import annotations

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QListWidget, QListWidgetItem, QWidget, QVBoxLayout


class AgentMonitorWidget(QWidget):
    DEFAULT_AGENTS = [
        "SystemAgent",
        "BrowserAgent",
        "ResearchAgent",
        "CodeAgent",
        "ProductivityAgent",
        "MediaAgent",
    ]

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._list = QListWidget(self)
        layout.addWidget(self._list)

        self._items: dict[str, QListWidgetItem] = {}
        for agent in self.DEFAULT_AGENTS:
            item = QListWidgetItem(f"{agent} - idle")
            self._set_item_color(item, "idle")
            self._list.addItem(item)
            self._items[agent] = item

    def update_agent(self, name: str, status: str) -> None:
        if name not in self._items:
            item = QListWidgetItem(f"{name} - {status}")
            self._list.addItem(item)
            self._items[name] = item
        item = self._items[name]
        item.setText(f"{name} - {status}")
        self._set_item_color(item, status)

    @staticmethod
    def _set_item_color(item: QListWidgetItem, status: str) -> None:
        palette = {
            "running": QColor("#22d3ee"),
            "complete": QColor("#34d399"),
            "failed": QColor("#fb7185"),
            "idle": QColor("#94a3b8"),
        }
        item.setForeground(palette.get(status, QColor("#94a3b8")))
