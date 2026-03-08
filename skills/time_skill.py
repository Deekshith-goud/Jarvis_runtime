from datetime import datetime


def handle_time(command: str) -> str:
    now = datetime.now()
    lower = command.lower()
    if "date" in lower:
        return "Today's date is " + now.strftime("%B %d, %Y")
    if "day" in lower:
        return "Today is " + now.strftime("%A")
    if "year" in lower:
        return "The year is " + str(now.year)
    return "The time is " + now.strftime("%I:%M %p")
