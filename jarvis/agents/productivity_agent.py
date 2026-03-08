from __future__ import annotations

import re
from datetime import datetime, timedelta
from typing import Any

from jarvis.core.agent import Agent


class ProductivityAgent(Agent):
    name = "productivity_agent"
    description = "Handles productivity intents like timers, tasks, and reminders."
    capabilities = ["set_timer", "check_timer", "cancel_timer", "create_task", "set_reminder"]

    def can_handle(self, intent: str) -> bool:
        return intent in self.capabilities

    async def execute(self, task: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        intent = task.get("intent", "")
        params = task.get("params", {}) or {}
        services = context.get("services", {})
        timer_manager = services.get("timer_manager")
        timer_callback = services.get("timer_callback")
        database = services.get("database")

        if intent == "set_timer":
            duration = int(params.get("duration", 0) or 0)
            if duration <= 0:
                return {
                    "agent": self.name,
                    "intent": intent,
                    "status": "failed",
                    "message": "Invalid timer duration.",
                    "params": params,
                }
            if timer_manager:
                timer_manager.set_timer(duration, timer_callback or (lambda: print("[TIMER] Timer finished.")))
                message = f"Timer set for {duration} seconds."
            else:
                message = "Timer manager unavailable."
            return {"agent": self.name, "intent": intent, "status": "completed", "message": message, "params": params}

        if intent == "check_timer":
            if not timer_manager:
                return {"agent": self.name, "intent": intent, "status": "failed", "message": "Timer manager unavailable."}
            remaining = timer_manager.get_remaining_time()
            if remaining <= 0:
                message = "There is no active timer."
            else:
                mins = int(remaining // 60)
                secs = int(remaining % 60)
                message = f"Timer has {mins} minute(s) and {secs} second(s) remaining."
            return {"agent": self.name, "intent": intent, "status": "completed", "message": message}

        if intent == "cancel_timer":
            if not timer_manager:
                return {"agent": self.name, "intent": intent, "status": "failed", "message": "Timer manager unavailable."}
            cancelled = timer_manager.cancel_timer()
            message = "Timer cancelled." if cancelled else "No active timer to cancel."
            return {"agent": self.name, "intent": intent, "status": "completed", "message": message}

        if intent == "create_task":
            text = str(params.get("text", "")).strip()
            if not text:
                return {"agent": self.name, "intent": intent, "status": "failed", "message": "Task text required."}
            if database:
                created = database.add_task(text)
                message = f"Task added: {text}" if created else "Task already exists."
            else:
                message = "Database unavailable."
            return {"agent": self.name, "intent": intent, "status": "completed", "message": message, "params": params}

        if intent == "set_reminder":
            text = str(params.get("text", "")).strip()
            message = "Reminder created."
            if database and text:
                match = re.search(r"remind me in (\d+)\s*minutes? to (.*)", text.lower())
                if match:
                    minutes = int(match.group(1))
                    remind_text = match.group(2).strip()
                    remind_time = (datetime.now() + timedelta(minutes=minutes)).strftime("%Y-%m-%d %H:%M:%S")
                    database.add_reminder(remind_text, remind_time)
                    message = f"Reminder set for {minutes} minute(s)."
                else:
                    message = "Reminder format: remind me in <minutes> to <message>."
            return {"agent": self.name, "intent": intent, "status": "completed", "message": message, "params": params}

        return {
            "agent": self.name,
            "intent": intent,
            "status": "failed",
            "message": f"Unsupported productivity intent: {intent}",
            "params": params,
        }
