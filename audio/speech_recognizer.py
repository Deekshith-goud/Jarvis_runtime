import time
import sounddevice as sd
import numpy as np
import speech_recognition as sr
import json
from vosk import KaldiRecognizer

from config.settings import SAMPLE_RATE, SILENCE_TIMEOUT


class SpeechRecognizer:
    def __init__(self, mic_manager, model=None):
        self._mic_manager = mic_manager
        self.recognizer = sr.Recognizer()
        self._vosk_model = model

    def recognize(self) -> str:
        while not self._mic_manager.is_enabled():
            time.sleep(0.1)

        print("[RECOGNIZER] Listening...")
        
        frames = []
        silence_threshold = 0.015  # RMS threshold for silence
        silent_chunks = 0
        started_speaking = False
        
        chunk_size = int(SAMPLE_RATE * 0.1)  # 100ms chunks
        
        # Record raw float32 audio and manually calculate energy to find silence
        with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype='float32') as stream:
            while True:
                if not self._mic_manager.is_enabled():
                    break
                    
                data, overflowed = stream.read(chunk_size)
                frames.append(data.copy())
                
                rms = np.sqrt(np.mean(data**2))
                
                if rms > silence_threshold:
                    if not started_speaking:
                        print("[RECOGNIZER] Hearing speech...")
                        started_speaking = True
                    silent_chunks = 0
                else:
                    if started_speaking:
                        silent_chunks += 1
                        
                # Wait for silence to indicate end of command
                if started_speaking and silent_chunks > (SILENCE_TIMEOUT / 0.1):
                    break

        if not frames:
            print("[RECOGNIZER] No audio captured.")
            return ""

        audio_data = np.concatenate(frames, axis=0)
        # Convert float32 array to int16 bytes for recognition engines
        audio_data_int16 = (audio_data * 32767).astype(np.int16)
        raw_bytes = audio_data_int16.tobytes()

        print("[RECOGNIZER] Processing speech...")
        
        # Try High Accuracy Google (requires internet)
        try:
            audio = sr.AudioData(raw_bytes, SAMPLE_RATE, 2)
            text = self.recognizer.recognize_google(audio)
            print("[RECOGNIZER] Google Final: " + text)
            return text.lower().strip()
            
        except sr.UnknownValueError:
            print("[RECOGNIZER] Google could not understand audio.")
        except sr.RequestError as e:
            print(f"[RECOGNIZER] Offline! Falling back to local Vosk model...")
            if self._vosk_model:
                try:
                    vosk_recognizer = KaldiRecognizer(self._vosk_model, SAMPLE_RATE)
                    vosk_recognizer.AcceptWaveform(raw_bytes)
                    result = json.loads(vosk_recognizer.FinalResult())
                    text = result.get("text", "").strip()
                    print("[RECOGNIZER] Vosk Final: " + text)
                    return text.lower()
                except Exception as ex:
                    print(f"[RECOGNIZER] Vosk fallback error: {ex}")
        except Exception as e:
            print(f"[RECOGNIZER] Error: {e}")
            
        return ""
