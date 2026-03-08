import argparse
import asyncio
import os
import sys
from typing import Any, List

from ai.ai_engine import AIEngine
from ai.ai_router import AIRouter
from ai.prompt_builder import PromptBuilder
from analytics.analytics_tracker import AnalyticsTracker
from audio.mic_manager import MicManager
from audio.speech_recognizer import SpeechRecognizer
from audio.tts_engine import TTSEngine
from audio.wake_listener import WakeListener
from config.config_manager import ConfigManager
from config.settings import AI_API_KEY, AI_BASE_URL, JARVIS_OUTPUT_DIR, VOSK_MODEL_PATH
from core.command_normalizer import normalize_command
from core.command_router import init_router
from jarvis.core.runtime import build_default_orchestrator
from memory.personal_memory import PersonalMemory
from memory.session_memory import SessionMemory
from productivity.focus_manager import FocusManager
from productivity.session_tracker import SessionTracker
from scheduler.reminder_scheduler import ReminderScheduler
from scheduler.timer_manager import TimerManager
from storage.database import DatabaseManager
from vosk import Model


class Runtime:
    def __init__(self) -> None:
        self._stop = False
        self.orchestrator = build_default_orchestrator()
        self.mic = MicManager()
        self.tts = TTSEngine(self.mic)
        self.db = DatabaseManager()
        self.timer_manager = TimerManager()
        self.personal_memory = PersonalMemory()
        self.session_memory = SessionMemory()
        self.focus_manager = FocusManager()
        self.session_tracker = SessionTracker(self.db)
        self.analytics_tracker = AnalyticsTracker(self.db)
        self.ai_router = AIRouter()
        self.prompt_builder = PromptBuilder()
        self.ai_engine = AIEngine(api_key=AI_API_KEY, base_url=AI_BASE_URL) if AI_API_KEY else None
        self.scheduler = ReminderScheduler(self.db, self._reminder_callback)
        self.scheduler.start()
        self.config_manager = ConfigManager()
        init_router(
            self.db,
            self.timer_manager,
            self._timer_callback,
            self.personal_memory,
            self.session_memory,
            self.ai_engine,
            self.ai_router,
            self.prompt_builder,
            self.focus_manager,
            self.session_tracker,
            self.analytics_tracker,
        )
        if not os.path.exists(JARVIS_OUTPUT_DIR):
            os.makedirs(JARVIS_OUTPUT_DIR)
        self._vosk_model = None

    def _timer_callback(self) -> None:
        self.tts.enqueue("Timer finished.", priority="high")

    def _reminder_callback(self, message: str) -> None:
        self.tts.enqueue("Reminder: " + message, priority="high")

    async def _run_orchestrator(self, normalized_command: str) -> List[str]:
        result = await self.orchestrator.handle_command(normalized_command)
        return self._extract_orchestrator_messages(result)

    @staticmethod
    def _extract_orchestrator_messages(result: dict[str, Any]) -> List[str]:
        messages: List[str] = []
        for task_id in sorted(result.get("results", {}).keys()):
            task_result = result["results"][task_id]
            if task_result.get("status") != "complete":
                messages.append(task_result.get("error", "Task failed."))
                continue
            payload = task_result.get("result", {})
            message = payload.get("message") or payload.get("response") or "Done."
            messages.append(message)
        return messages

    @staticmethod
    def _orchestrator_has_success(result: dict[str, Any]) -> bool:
        summary = result.get("summary", {}) if isinstance(result, dict) else {}
        return int(summary.get("successful_tasks", 0) or 0) > 0

    def process_command(self, command: str) -> List[str]:
        _, normalized = normalize_command(command)
        alias_response = self._handle_alias_commands(command, normalized)
        if alias_response is not None:
            return [alias_response]

        if normalized in {"stop", "shut up"}:
            self.tts.interrupt()
            return ["Stopped speaking."]

        orchestrator_result = asyncio.run(self.orchestrator.handle_command(normalized))
        orchestrator_messages = self._extract_orchestrator_messages(orchestrator_result)
        if self._orchestrator_has_success(orchestrator_result):
            return orchestrator_messages or ["Done."]
        return orchestrator_messages or ["I did not understand the command."]

    def _handle_alias_commands(self, original: str, normalized: str) -> str | None:
        if normalized == "list app aliases":
            aliases = self.config_manager.get("app_aliases", {}) or {}
            if not aliases:
                return "No app aliases configured."
            lines = ["App aliases:"]
            for key in sorted(aliases.keys()):
                lines.append(f"- {key}: {aliases[key]}")
            return "\n".join(lines)

        if normalized.startswith("add app alias "):
            parts = original.strip().split(maxsplit=4)
            if len(parts) < 5:
                return "Format: add app alias <name> <full_path_or_executable>"
            name = parts[3].strip().lower()
            target = parts[4].strip().strip('"')
            if not name or not target:
                return "Format: add app alias <name> <full_path_or_executable>"
            config = self.config_manager.config
            aliases = config.get("app_aliases", {}) or {}
            aliases[name] = target
            config["app_aliases"] = aliases
            with open(self.config_manager.config_file, "w", encoding="utf-8") as handle:
                import json

                json.dump(config, handle, indent=4)
            self.config_manager.config = config
            return f"Alias added: {name} -> {target}"

        if normalized.startswith("remove app alias "):
            name = normalized.replace("remove app alias ", "", 1).strip().lower()
            config = self.config_manager.config
            aliases = config.get("app_aliases", {}) or {}
            if name not in aliases:
                return f"Alias '{name}' not found."
            aliases.pop(name, None)
            config["app_aliases"] = aliases
            with open(self.config_manager.config_file, "w", encoding="utf-8") as handle:
                import json

                json.dump(config, handle, indent=4)
            self.config_manager.config = config
            return f"Alias removed: {name}"
        return None

    def _emit(self, source: str, messages: List[str], print_output: bool = True) -> None:
        seen = set()
        for msg in messages:
            clean = " ".join(str(msg).split())
            if not clean or clean in seen:
                continue
            seen.add(clean)
            if print_output:
                print(clean)
            self.tts.enqueue(clean)
            self.session_memory.update(source, clean)

    def _load_voice_components(self) -> tuple[WakeListener, SpeechRecognizer]:
        if self._vosk_model is None:
            self._vosk_model = Model(VOSK_MODEL_PATH)
        wake = WakeListener(self.mic, self._vosk_model)
        recog = SpeechRecognizer(self.mic, self._vosk_model)
        return wake, recog

    def _run_terminal_mode(self) -> str:
        print("[MODE] Terminal mode active.")
        while not self._stop:
            command = input("> ").strip()
            if not command:
                continue
            lower = command.lower()
            if lower == "exit":
                self._stop = True
                self.tts.enqueue("Jarvis Runtime stopped.")
                return "exit"
            if lower in {"switch to voice", "voice mode"}:
                self.tts.enqueue("Switching to voice mode.")
                return "voice"
            if lower in {"switch to terminal", "terminal mode"}:
                print("Already in terminal mode.")
                continue
            if lower == "jarvis":
                self.tts.enqueue("Yes, I am listening.")
                print("Yes, I am listening.")
                continue
            self._emit(command, self.process_command(command), print_output=True)
        return "exit"

    def _run_voice_mode(self) -> str:
        print("[MODE] Voice mode active. Say wake word.")
        try:
            wake, recognizer = self._load_voice_components()
        except Exception as exc:
            print(f"[VOICE] Failed to start voice mode: {exc}")
            self.tts.enqueue("Voice mode is unavailable. Returning to terminal mode.")
            return "terminal"

        asleep = True
        while not self._stop:
            if asleep:
                detected = wake.listen()
                if not detected:
                    continue
                self.tts.enqueue(self.tts.get_greeting())
                asleep = False
                continue

            spoken = recognizer.recognize().strip()
            if not spoken:
                continue
            lower = spoken.lower()
            if lower == "exit":
                self._stop = True
                self.tts.enqueue("Jarvis Runtime stopped.")
                return "exit"
            if lower in {"switch to terminal", "terminal mode"}:
                self.tts.enqueue("Switching to terminal mode.")
                return "terminal"
            if lower in {"switch to voice", "voice mode"}:
                self.tts.enqueue("Already in voice mode.")
                continue
            if lower == "sleep":
                self.tts.enqueue("Going to sleep.")
                asleep = True
                continue
            self._emit(spoken, self.process_command(spoken), print_output=False)
        return "exit"

    def run(self, mode: str = "terminal") -> None:
        print("Jarvis Runtime started.")
        self.tts.enqueue(self.tts.get_greeting())
        current_mode = mode
        while not self._stop:
            if current_mode == "voice":
                current_mode = self._run_voice_mode()
            else:
                current_mode = self._run_terminal_mode()
            if current_mode == "exit":
                break
        self.shutdown()

    def shutdown(self) -> None:
        self._stop = True
        self.scheduler.stop()
        self.tts.stop()


def main() -> None:
    parser = argparse.ArgumentParser(description="Jarvis Runtime")
    parser.add_argument("--voice", action="store_true", help="Start directly in voice mode")
    args = parser.parse_args()

    runtime = Runtime()
    try:
        runtime.run(mode="voice" if args.voice else "terminal")
    except (KeyboardInterrupt, SystemExit):
        runtime.shutdown()
        print("Jarvis Runtime stopped.")
        sys.exit(0)


if __name__ == "__main__":
    main()
