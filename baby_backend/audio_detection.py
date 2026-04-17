# audio_detection.py

import sounddevice as sd
import numpy as np
from cry_model import extract_features, classify_sound
from config import SAMPLE_RATE, DURATION, AUDIO_DEVICE

# Set laptop mic
sd.default.device = (AUDIO_DEVICE, None)

def detect_sound_background(callback):
    def run():
        try:
            print("[audio] Listening...")

            audio = sd.rec(int(DURATION * SAMPLE_RATE),
                           samplerate=SAMPLE_RATE,
                           channels=1)
            sd.wait()

            # Ignore very low sound (silence/noise)
            if np.max(audio) < 0.01:
                return

            features = extract_features(audio, SAMPLE_RATE)
            result = classify_sound(features)

            print("Prediction:", result)

            if result == "cry" or result == "uncertain":
                print("[audio] Possible Cry Detected!")
                callback(True)

        except Exception as e:
            print("[audio] Audio Error:", e)

    return run