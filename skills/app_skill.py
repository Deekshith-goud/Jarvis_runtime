import os
import platform
import shutil
import subprocess
from config.config_manager import ConfigManager

try:
    import winreg  # type: ignore[attr-defined]
except Exception:
    winreg = None


def _find_windows_app_path(exe_name: str) -> str | None:
    if winreg is None:
        return None
    candidates = [exe_name, exe_name + ".exe"] if not exe_name.lower().endswith(".exe") else [exe_name]
    for candidate in candidates:
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, rf"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\{candidate}") as key:
                value, _ = winreg.QueryValueEx(key, None)
                if value and os.path.exists(value):
                    return value
        except Exception:
            pass
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, rf"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\{candidate}") as key:
                value, _ = winreg.QueryValueEx(key, None)
                if value and os.path.exists(value):
                    return value
        except Exception:
            pass
    return None


def handle_app(command: str) -> str:
    lower = command.lower()
    system = platform.system()
    config = ConfigManager()
    custom_aliases = config.get("app_aliases", {}) or {}

    # Extract the app name
    app_name = lower.replace("open app", "").replace("launch app", "").replace("start app", "")
    app_name = app_name.replace("open ", "").replace("launch ", "").replace("start ", "").strip()
    
    if not app_name:
        return "No application specified."

    # Map common descriptive names to their executables or URIs
    app_map = {
        "notepad": "notepad",
        "calculator": "calc",
        "calc": "calc",
        "chrome": "chrome",
        "browser": "chrome",
        "microsoft store": "ms-windows-store:",
        "store": "ms-windows-store:",
        "cursor": "cursor",
        "vscode": "code",
        "visual studio code": "code",
        "code": "code",
        "word": "winword",
        "excel": "excel",
        "powerpoint": "powerpnt",
        "spotify": "spotify",
        "discord": "discord",
        "slack": "slack",
        "notion": "notion",
        "tlauncher": "tlauncher",
        "whatsapp": "whatsapp",
    }

    merged_aliases = {**app_map, **{k.lower(): v for k, v in custom_aliases.items()}}
    exe_name = merged_aliases.get(app_name, app_name)

    # Direct path handling first.
    if os.path.exists(exe_name):
        try:
            if system == "Windows":
                os.startfile(exe_name)  # type: ignore[attr-defined]
            else:
                subprocess.Popen([exe_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return f"Opening {app_name.title()}."
        except Exception:
            return f"Failed to open {app_name.title()}."

    # URI schemes like ms-windows-store:, whatsapp:
    if ":" in exe_name and not os.path.exists(exe_name):
        try:
            if system == "Windows":
                os.startfile(exe_name)  # type: ignore[attr-defined]
                return f"Opening {app_name.title()}."
        except Exception:
            return f"Failed to open {app_name.title()}."

    resolved = shutil.which(exe_name)
    if not resolved and system == "Windows":
        resolved = _find_windows_app_path(exe_name)

    if not resolved and exe_name == app_name:
        # Last try for app execution aliases on Windows.
        if system == "Windows":
            try:
                subprocess.Popen(
                    f'start "" "{exe_name}"',
                    shell=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                return f"Opening {app_name.title()}."
            except Exception:
                pass
        return f"Application '{app_name}' not found. Add path in config.json -> app_aliases."

    if system == "Windows":
        try:
            target = resolved or exe_name
            subprocess.Popen(
                ["cmd", "/c", "start", "", target],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return f"Opening {app_name.title()}."
        except Exception:
            return f"Failed to open {app_name.title()}."
    elif system == "Darwin":
        try:
            subprocess.Popen(["open", "-a", app_name.title()], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return f"Opening {app_name.title()}."
        except Exception:
            return f"Failed to open {app_name.title()}."
    else:
        try:
            subprocess.Popen([resolved or exe_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return f"Opening {app_name.title()}."
        except Exception:
            return "Unknown application."
