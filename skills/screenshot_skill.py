import pyautogui
from datetime import datetime


def handle_screenshot(command: str = "") -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = "screenshot_" + timestamp + ".png"
    image = pyautogui.screenshot()
    image.save(filename)
    return "Screenshot saved as " + filename
