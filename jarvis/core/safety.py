from __future__ import annotations

import re
from pathlib import Path
from typing import Any


class SafetyValidator:
    def __init__(self, allowed_app_paths: list[str] | None = None) -> None:
        self.allowed_app_paths = [
            Path(path).resolve() for path in (allowed_app_paths or self._default_allowed_app_paths())
        ]
        self._dangerous_intents = {"delete_system_files", "format_disk", "rm_rf_root"}
        self._confirm_required_intents = {"shutdown_system"}
        self._injection_patterns = [
            r";",
            r"&&",
            r"\|\|",
            r"`",
            r"\$\(",
            r"\.\./",
            r"\.\.\\",
            r"\brm\s+-rf\s+/\b",
            r"\bformat\s+disk\b",
            r"\bshutdown\b",
            r"\bdel\s+/f\b",
        ]

    def validate_task(self, task: Any) -> tuple[bool, str]:
        intent = str(getattr(task, "intent", "")).strip()
        params = getattr(task, "params", {})
        valid, reason = self._validate_params_shape(params)
        if not valid:
            return False, reason
        if intent in self._dangerous_intents:
            return False, f"Blocked dangerous intent '{intent}'"
        if intent in self._confirm_required_intents and params.get("confirmed") is not True:
            return False, f"Intent '{intent}' requires explicit confirmation"
        valid, reason = self._validate_timer(intent, params)
        if not valid:
            return False, reason
        valid, reason = self._check_injection(params)
        if not valid:
            return False, reason
        valid, reason = self._validate_allowed_app_path(intent, params)
        if not valid:
            return False, reason
        return True, ""

    @staticmethod
    def _validate_params_shape(params: Any) -> tuple[bool, str]:
        if params is None:
            return True, ""
        if not isinstance(params, dict):
            return False, "Task params must be a dictionary"
        return True, ""

    @staticmethod
    def _validate_timer(intent: str, params: dict[str, Any]) -> tuple[bool, str]:
        if intent != "set_timer":
            return True, ""
        duration = params.get("duration")
        if duration is None:
            return True, ""
        if not isinstance(duration, int):
            return False, "Timer duration must be an integer (seconds)"
        if duration <= 0:
            return False, "Timer duration must be greater than zero"
        if duration > 24 * 60 * 60:
            return False, "Timer duration exceeds allowed limit"
        return True, ""

    def _check_injection(self, params: dict[str, Any]) -> tuple[bool, str]:
        for key, value in params.items():
            if isinstance(value, str):
                for pattern in self._injection_patterns:
                    if re.search(pattern, value, flags=re.IGNORECASE):
                        return False, f"Potential command injection detected in '{key}'"
        return True, ""

    def _validate_allowed_app_path(self, intent: str, params: dict[str, Any]) -> tuple[bool, str]:
        if intent != "open_app":
            return True, ""
        target = params.get("target") or params.get("text")
        if not isinstance(target, str) or not target.strip() or not self._looks_like_path(target):
            return True, ""
        path = Path(target).expanduser().resolve()
        if any(self._is_within(path, allowed) for allowed in self.allowed_app_paths):
            return True, ""
        return False, f"Application path is not allowed: '{target}'"

    @staticmethod
    def _looks_like_path(value: str) -> bool:
        return (
            value.startswith(("/", "\\"))
            or ":" in value
            or "/" in value
            or "\\" in value
            or value.endswith(".exe")
        )

    @staticmethod
    def _is_within(path: Path, parent: Path) -> bool:
        try:
            path.relative_to(parent)
            return True
        except ValueError:
            return False

    @staticmethod
    def _default_allowed_app_paths() -> list[str]:
        return [r"C:\Program Files", r"C:\Program Files (x86)", r"C:\Windows\System32"]
