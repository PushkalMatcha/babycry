# cry_model.py

import librosa
import numpy as np
import joblib

# Load trained model
model = joblib.load("cry_model.pkl")

def extract_features(audio, sr):
    mfccs = librosa.feature.mfcc(y=audio.flatten(), sr=sr, n_mfcc=40)
    return np.mean(mfccs.T, axis=0).reshape(1, -1)

def classify_sound(features):
    probs = model.predict_proba(features)
    confidence = np.max(probs)

    # Ignore low confidence predictions
    if confidence < 0.55:
        return "uncertain"

    prediction = model.predict(features)
    return prediction[0]