import threading
import queue
import random
import pyttsx3
from config.settings import TTS_VOICE, TTS_RATE


HIGH = 0
NORMAL = 1

_counter_lock = threading.Lock()
_counter = 0


def _next_counter():
    global _counter
    with _counter_lock:
        _counter += 1
        return _counter


class TTSEngine:
    def __init__(self, mic_manager):
        self._mic_manager = mic_manager
        self._queue = queue.PriorityQueue()
        self._running = True
        self._speaking = False
        self._current_engine = None

        # Single daemon worker thread
        self._worker = threading.Thread(target=self._run_worker, daemon=True)
        self._worker.start()

    def enqueue(self, text: str, priority: str = "normal"):
        print("[TTS] " + text)
        pri = HIGH if priority == "high" else NORMAL

        if pri == HIGH:
            self._drain_normal()

        count = _next_counter()
        self._queue.put((pri, count, text))

    def speak(self, text: str):
        """Backward-compatible wrapper."""
        self.enqueue(text, priority="normal")

    def interrupt(self):
        """Stop current speech and clear queue."""
        # Clear queue
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
            except queue.Empty:
                break
        
        # Stop current engine if speaking
        if self._current_engine and self._speaking:
            try:
                self._current_engine.stop()
            except Exception:
                pass

    def get_greeting(self) -> str:
        greetings = [
            "Yes?",
            "I'm here.",
            "Listening.",
            "What do you need?",
            "How can I help?",
            "Ready."
        ]
        return random.choice(greetings)

    def _drain_normal(self):
        """Remove pending normal-priority items, keep high-priority."""
        drained = []
        while not self._queue.empty():
            try:
                item = self._queue.get_nowait()
                if item[0] == HIGH:
                    drained.append(item)
            except queue.Empty:
                break
        for item in drained:
            self._queue.put(item)

    def _speak_one(self, text):
        """Create a fresh pyttsx3 engine, speak, and dispose."""
        try:
            self._current_engine = pyttsx3.init()
            self._current_engine.setProperty("rate", TTS_RATE)

            voices = self._current_engine.getProperty('voices')
            for voice in voices:
                if TTS_VOICE.lower() in voice.name.lower() or TTS_VOICE == voice.id:
                    self._current_engine.setProperty('voice', voice.id)
                    break

            self._current_engine.say(text)
            self._current_engine.runAndWait()
            self._current_engine.stop()
        except Exception as e:
            print("[TTS] Error: " + str(e))
        finally:
            self._current_engine = None

    def _run_worker(self):
        while self._running:
            try:
                pri, count, text = self._queue.get(timeout=0.5)
            except queue.Empty:
                continue

            self._mic_manager.disable_mic()
            self._speaking = True
            try:
                self._speak_one(text)
            finally:
                self._speaking = False
                self._mic_manager.enable_mic()

    def stop(self):
        self._running = False
        if self._worker.is_alive():
            self._worker.join(timeout=3)
