class StateManager:
    SLEEP = "SLEEP"
    ACTIVE = "ACTIVE"
    LISTENING = "LISTENING"
    PROCESSING = "PROCESSING"
    SPEAKING = "SPEAKING"

    def __init__(self):
        self._state = self.SLEEP

    def set_state(self, state: str):
        self._state = state

    def get_state(self) -> str:
        return self._state
