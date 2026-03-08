# MOCK FASTTEXT FOR WINDOWS C++ BUILD TOOLS MISSING FALLBACK
import os

class ModelMock:
    def predict(self, text, k=1):
        t = text.lower()
        if any(w in t for w in ["study environment", "workspace", "zen mode", "focus", "distraction"]):
            return (["__label__focus"], [0.9])
        if any(w in t for w in ["help with", "explain", "how do i", "what does", "teach me"]):
            return (["__label__explain"], [0.85])
        if any(w in t for w in ["countdown", "remind me in", "warning in", "timer"]):
            return (["__label__timer"], [0.88])
        if any(w in t for w in ["status", "health", "uptime"]):
            return (["__label__health"], [0.95])
        return (["__label__unknown"], [0.3])
        
    def save_model(self, path):
        pass

def train_supervised(*args, **kwargs):
    return ModelMock()

def load_model(path):
    return ModelMock()

class FastText:
    eprint = lambda x: None
