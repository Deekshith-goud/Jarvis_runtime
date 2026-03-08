class ModeManager:
    VOICE = "voice"
    TERMINAL = "terminal"

    def __init__(self):
        self._mode = self.TERMINAL

    def switch_to_voice(self):
        self._mode = self.VOICE

    def switch_to_terminal(self):
        self._mode = self.TERMINAL

    def get_mode(self) -> str:
        return self._mode
