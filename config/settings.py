import os

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_FILE = os.path.join(_BASE_DIR, "config.json")

WAKE_WORD = "jarvis"
VOSK_MODEL_PATH = os.path.join(_BASE_DIR, "model")
SAMPLE_RATE = 16000
BLOCK_SIZE = 8000
SILENCE_TIMEOUT = 0.7

# Text-to-Speech Settings
# Set to 'zira' for female, 'david' for male. 
# You can also pass a full Voice ID string here if you install more.
TTS_VOICE = "hazel" 
TTS_RATE = 175

# AI Settings (Google Gemini)
AI_API_KEY = "AIzaSyDTAlxcaXfbedEqQCe0ZHBQSuMvsG1q5u8"  # Set your Gemini API key here
AI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

# Jarvis output folder (on Desktop)
JARVIS_OUTPUT_DIR = os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop", "Jarvis")
