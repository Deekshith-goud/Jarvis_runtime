import os
import sys

try:
    import psutil
except ImportError:
    psutil = None

LOCK_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "runtime.lock")

def _check_pid_running(pid: int) -> bool:
    if psutil:
        return psutil.pid_exists(pid)
    else:
        try:
            if sys.platform == "win32":
                # os.kill(pid, 0) is not reliable on Windows. 
                # Alternative without psutil:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                SYNCHRONIZE = 0x00100000
                process = kernel32.OpenProcess(SYNCHRONIZE, 0, pid)
                if process != 0:
                    kernel32.CloseHandle(process)
                    return True
                return False
            else:
                os.kill(pid, 0)
                return True
        except OSError:
            return False
            
def acquire_lock() -> bool:
    try:
        current_pid = os.getpid()
        if os.path.exists(LOCK_FILE):
            try:
                with open(LOCK_FILE, 'r') as f:
                    old_pid = int(f.read().strip())
                if _check_pid_running(old_pid):
                    return False
                else:
                    os.remove(LOCK_FILE)
            except (ValueError, OSError):
                try:
                    os.remove(LOCK_FILE)
                except OSError:
                    pass
                    
        with open(LOCK_FILE, 'w') as f:
            f.write(str(current_pid))
        return True
    except Exception:
        return False

def release_lock():
    try:
        if os.path.exists(LOCK_FILE):
            os.remove(LOCK_FILE)
    except OSError:
        pass
