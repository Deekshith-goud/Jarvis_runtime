from __future__ import annotations

import os
import platform
import shutil
import subprocess
from typing import Any

from jarvis.core.agent import Agent
from skills.web_skill import handle_web


class SystemAgent(Agent):
    name = "system_agent"
    description = "Handles local system launch actions."
    capabilities = ["open_app", "open_website"]
    _app_map = {
        "notepad": "notepad",
        "calculator": "calc",
        "calc": "calc",
        "chrome": "chrome",
        "browser": "chrome",
        "cursor": "cursor",
        "vscode": "code",
        "visual studio code": "code",
        "code": "code",
        "spotify": "spotify",
        "discord": "discord",
        "slack": "slack",
    }

    def can_handle(self, intent: str) -> bool:
        return intent in self.capabilities

    async def execute(self, task: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        intent = task.get("intent", "")
        params = task.get("params", {}) or {}
        target = params.get("target") or params.get("text") or ""
        if intent == "open_website":
            message = handle_web(f"open {target}".strip())
        else:
            message = self._open_application(target)
        return {
            "agent": self.name,
            "intent": intent,
            "status": "completed",
            "message": message,
            "params": params,
        }

    def _open_application(self, target: str) -> str:
        app_name = target.strip().lower()
        if not app_name:
            return "No application specified."

        executable = self._app_map.get(app_name, app_name)
        is_path = any(token in executable for token in (":\\", "/", "\\"))
        exists = os.path.exists(executable) if is_path else (shutil.which(executable) is not None)
        if not exists and executable == app_name:
            return f"Application '{target}' not found."

        system = platform.system()
        try:
            if system == "Windows":
                subprocess.Popen(
                    ["cmd", "/c", "start", "", executable],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            elif system == "Darwin":
                subprocess.Popen(["open", "-a", executable], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                subprocess.Popen([executable], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return f"Opening {target.title()}."
        except Exception:
            return f"Failed to open {target.title()}."
