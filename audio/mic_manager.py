class MicManager:
    def __init__(self):
        self._mic_enabled = True

    def enable_mic(self):
        self._mic_enabled = True

    def disable_mic(self):
        self._mic_enabled = False

    def is_enabled(self) -> bool:
        return self._mic_enabled
