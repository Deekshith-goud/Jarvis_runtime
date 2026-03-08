import os
import sys

# Windows missing C++ tools fallback
try:
    import fasttext
except ImportError:
    import nlu.fasttext as fasttext
_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(_DIR, "intent_model.bin")

class IntentClassifier:
    def __init__(self):
        self.model = None

    def load_model(self):
        if self.model is None:
            if os.path.exists(MODEL_PATH):
                # fasttext output suppresses annoying warnings using silent mode if available
                # but we will just load it normally
                fasttext.FastText.eprint = lambda x: None # suppress silent warnings
                self.model = fasttext.load_model(MODEL_PATH)

    def classify(self, text: str) -> tuple[str, float]:
        self.load_model()
        if not self.model:
            return ("", 0.0)
            
        # Clean text
        text = text.lower().strip()
        labels, probabilities = self.model.predict(text, k=1)
        
        if labels and probabilities:
            # removing '__label__' prefix
            intent = labels[0].replace("__label__", "")
            return (intent, probabilities[0])
        return ("", 0.0)
