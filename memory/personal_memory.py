import json
import os
from datetime import datetime


_MEMORY_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "personal_memory.json")


class PersonalMemory:
    def __init__(self):
        self._memories = []
        self._load()

    def _load(self):
        if os.path.exists(_MEMORY_FILE):
            try:
                with open(_MEMORY_FILE, "r", encoding="utf-8") as f:
                    self._memories = json.load(f)
            except (json.JSONDecodeError, IOError):
                self._memories = []

    def _save(self):
        with open(_MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(self._memories, f, indent=2, ensure_ascii=False)

    def _next_id(self):
        if not self._memories:
            return 1
        return max(m["id"] for m in self._memories) + 1

    def add_memory(self, content: str) -> str:
        entry = {
            "id": self._next_id(),
            "content": content.strip(),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self._memories.append(entry)
        self._save()
        return "Remembered: " + entry["content"]

    def list_memories(self) -> str:
        if not self._memories:
            return "No memories stored."
        lines = []
        for m in self._memories:
            lines.append("[" + str(m["id"]) + "] " + m["content"] + " (" + m["created_at"] + ")")
        return "\n".join(lines)

    def search_memories(self, keyword: str) -> str:
        keyword_lower = keyword.lower()
        results = [m for m in self._memories if keyword_lower in m["content"].lower()]
        if not results:
            return "No memories found for: " + keyword
        lines = []
        for m in results:
            lines.append("[" + str(m["id"]) + "] " + m["content"] + " (" + m["created_at"] + ")")
        return "\n".join(lines)

    def delete_memory(self, memory_id: int) -> str:
        for i, m in enumerate(self._memories):
            if m["id"] == memory_id:
                removed = self._memories.pop(i)
                self._save()
                return "Deleted memory: " + removed["content"]
        return "No memory found with ID " + str(memory_id)
