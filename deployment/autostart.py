import os
import sys
import winreg

def _get_main_script_path():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, "main.py")

def enable_autostart():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        python_exe = sys.executable
        script_path = _get_main_script_path()
        value = f'"{python_exe}" "{script_path}" --daemon'
        winreg.SetValueEx(key, "JarvisRuntime", 0, winreg.REG_SZ, value)
        winreg.CloseKey(key)
        return True, "Auto start enabled."
    except Exception as e:
        return False, f"Failed to enable auto start: {e}"

def disable_autostart():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        winreg.DeleteValue(key, "JarvisRuntime")
        winreg.CloseKey(key)
        return True, "Auto start disabled."
    except FileNotFoundError:
        return True, "Auto start is already disabled."
    except Exception as e:
        return False, f"Failed to disable auto start: {e}"
