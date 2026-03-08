import json
import time
import sounddevice as sd
from vosk import Model, KaldiRecognizer

from config.settings import VOSK_MODEL_PATH, SAMPLE_RATE, BLOCK_SIZE, WAKE_WORD


class WakeListener:
    def __init__(self, mic_manager, model=None):
        self._mic_manager = mic_manager
        if model:
            self._model = model
        else:
            self._model = Model(VOSK_MODEL_PATH)

    def listen(self) -> bool:
        recognizer = KaldiRecognizer(self._model, SAMPLE_RATE)
        print("[WAKE] Listening for '" + WAKE_WORD + "'...")
        with sd.RawInputStream(samplerate=SAMPLE_RATE, blocksize=BLOCK_SIZE,
                               dtype="int16", channels=1, device=None) as stream:
            while True:
                if not self._mic_manager.is_enabled():
                    time.sleep(0.1)
                    continue
                data, overflowed = stream.read(BLOCK_SIZE)
                audio_bytes = bytes(data)
                if recognizer.AcceptWaveform(audio_bytes):
                    result = json.loads(recognizer.Result())
                    text = result.get("text", "").lower()
                    if text:
                        print("[WAKE] Heard:", text)
                    if WAKE_WORD in text:
                        return True
                else:
                    partial = json.loads(recognizer.PartialResult())
                    text = partial.get("partial", "").lower()
                    if text and WAKE_WORD in text:
                        print("[WAKE] Partial match:", text)
                        return True
