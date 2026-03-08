import re

class AIGuard:
    @staticmethod
    def requires_confirmation(filename: str) -> bool:
        exts = [".py", ".exe", ".bat", ".ps1", ".sh"]
        for ext in exts:
            if filename.lower().endswith(ext):
                return True
        return False

    @staticmethod
    def sanitize_filename(name: str) -> str:
        # Remove special characters, replace spaces with underscores, lowercase
        sanitized = re.sub(r'[^\w\s-]', '', name)
        sanitized = sanitized.replace(' ', '_').lower()
        # Max length 50 chars
        if len(sanitized) > 50:
            sanitized = sanitized[:50]
        return sanitized

    @staticmethod
    def should_speak_full_output(text: str) -> bool:
        return len(text) <= 400
