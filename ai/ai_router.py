_LANG_EXTENSIONS = {
    "python": ".py", "py": ".py",
    "javascript": ".js", "js": ".js",
    "java": ".java",
    "c++": ".cpp", "cpp": ".cpp",
    "c#": ".cs", "csharp": ".cs",
    "c": ".c",
    "html": ".html",
    "css": ".css",
    "ruby": ".rb",
    "go": ".go", "golang": ".go",
    "rust": ".rs",
    "typescript": ".ts", "ts": ".ts",
    "php": ".php",
    "swift": ".swift",
    "kotlin": ".kt",
    "bash": ".sh", "shell": ".sh",
    "sql": ".sql",
    "r": ".r",
    "matlab": ".m",
    "perl": ".pl",
    "lua": ".lua",
    "dart": ".dart",
    "scala": ".scala"
}


class AIRouter:
    _KEYWORDS = {
        "code": ["write code", "create program", "write program", "create a program",
                 "write a program", "code for", "script for", "write script",
                 "write a script", "create script", "create a script",
                 "program for", "program on", "program to",
                 "write a function", "create a function", "implement"],
        "draft": ["draft", "write document", "compose", "create document"],
        "research": ["research", "investigate", "look up", "look into"],
        "analyze": ["analyze", "analysis", "compare", "comparison", "versus", "vs"],
        "explain": ["explain", "what is", "what are", "how does", "how do",
                     "tell me about", "describe", "difference between"],
        "plan": ["plan", "strategy", "roadmap", "action plan",
                 "steps to", "how to achieve", "how to learn", "schedule for"],
        "notes": ["notes", "summarize", "summary", "study notes",
                  "create notes", "make notes"]
    }

    def route(self, command: str) -> str:
        lower = command.lower()
        # Check in priority order — more specific first
        for task_type in ["code", "analyze", "plan", "draft", "research", "notes", "explain"]:
            keywords = self._KEYWORDS[task_type]
            for keyword in keywords:
                if keyword in lower:
                    return task_type
        return "explain"

    def detect_language(self, command: str) -> str:
        """Detect programming language from command, default to python."""
        lower = command.lower()
        # Check for explicit language mentions
        for lang, ext in _LANG_EXTENSIONS.items():
            # Match "in python", "in java", "using javascript", etc.
            if " in " + lang in lower or " using " + lang in lower or " with " + lang in lower:
                return ext
        return ".py"

    def get_format(self, task_type: str, command: str) -> str:
        """Return the file extension based on task type and command context."""
        if task_type == "code":
            return self.detect_language(command)
        elif task_type == "notes":
            return ".txt"
        elif task_type == "analyze":
            return ".xlsx"
        else:
            # draft, research, plan → .docx
            return ".docx"
