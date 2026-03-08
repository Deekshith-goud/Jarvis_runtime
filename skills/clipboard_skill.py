import pyperclip


def handle_clipboard(command: str) -> str:
    lower = command.lower()
    if "read" in lower:
        content = pyperclip.paste()
        if not content:
            return "Clipboard is empty."
        return "Clipboard contains: " + content
    if "copy" in lower:
        text = command.lower().replace("copy ", "", 1).strip()
        if not text:
            return "Nothing to copy."
        pyperclip.copy(text)
        return "Copied to clipboard."
    return "Unknown clipboard command."
