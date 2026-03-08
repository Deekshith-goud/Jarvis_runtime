import os
from datetime import datetime
from config.config_manager import ConfigManager

_config = ConfigManager()

def _get_log_dir():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, "logs")

def _write_log(level: str, message: str):
    log_dir = _get_log_dir()
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    log_file = os.path.join(log_dir, "runtime.log")
    
    max_size_kb = _config.get("log_max_size_kb", 512)
    if os.path.exists(log_file) and os.path.getsize(log_file) > max_size_kb * 1024:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        rotated_file = os.path.join(log_dir, f"runtime_{timestamp}.log")
        os.rename(log_file, rotated_file)
        
    timestamp_log = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp_log}] [{level}] {message}\n")

def log_info(message: str):
    _write_log("INFO", message)

def log_error(message: str):
    _write_log("ERROR", message)
