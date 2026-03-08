from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from jarvis_app.event_bridge import EventBridge
from jarvis_app.main_window import MainWindow
from jarvis_app.state_manager import AppStateManager


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Jarvis Desktop")

    state_manager = AppStateManager()
    bridge = EventBridge()
    window = MainWindow(bridge=bridge, state_manager=state_manager)
    window.show()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
