import threading
import time

class TimerManager:
    def __init__(self):
        self._timer = None
        self._target_time = 0

    def set_timer(self, seconds: float, callback):
        if self._timer and self._timer.is_alive():
            self._timer.cancel()
        self._target_time = time.time() + seconds
        self._timer = threading.Timer(seconds, self._on_finish, args=(callback,))
        self._timer.daemon = True
        self._timer.start()

    def _on_finish(self, callback):
        self._target_time = 0
        callback()

    def cancel_timer(self):
        if self._timer and self._timer.is_alive():
            self._timer.cancel()
            self._target_time = 0
            return True
        return False

    def get_remaining_time(self) -> float:
        if self._target_time == 0:
            return 0
        rem = self._target_time - time.time()
        return rem if rem > 0 else 0
