import os
import fasttext

_DIR = os.path.dirname(os.path.abspath(__file__))
TRAIN_DATA = os.path.join(_DIR, "intent_training.txt")
MODEL_OUT = os.path.join(_DIR, "intent_model.bin")

def train():
    print(f"Training fasttext model using {TRAIN_DATA}...")
    model = fasttext.train_supervised(input=TRAIN_DATA, epoch=50, wordNgrams=2)
    model.save_model(MODEL_OUT)
    print(f"Model saved to {MODEL_OUT}")
    
if __name__ == "__main__":
    train()
