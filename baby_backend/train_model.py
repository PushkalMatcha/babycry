import librosa
import numpy as np
import os
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
import joblib
from config import SAMPLE_RATE

DATASET_PATH = "dataset"

def extract_features(file_path):
    try:
        audio, sr = librosa.load(file_path, sr=SAMPLE_RATE)
        mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=40)
        return np.mean(mfccs.T, axis=0)
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return None

features = []
labels = []

print("🚀 Starting dataset loading...")

for label in ["cry", "normal"]:
    folder = os.path.join(DATASET_PATH, label)

    if not os.path.exists(folder):
        print(f"❌ Folder not found: {folder}")
        continue

    print(f"\n📂 Reading folder: {folder}")

    for file in os.listdir(folder):
        path = os.path.join(folder, file)

        data = extract_features(path)

        if data is not None:
            features.append(data)
            labels.append(label)
            print("✅ Loaded:", file)
        else:
            print("⚠️ Skipped:", file)

# Convert to numpy
X = np.array(features)
y = np.array(labels)

print("\n📊 Dataset Summary:")
print("Total samples:", len(X))
print("Cry samples:", list(y).count("cry"))
print("Normal samples:", list(y).count("normal"))

# Check if enough data
if len(X) < 10:
    print("❌ Not enough data to train model!")
    exit()

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print("\n🧠 Training model...")

model = SVC(kernel='linear', probability=True)
model.fit(X_train, y_train)

# Evaluate
accuracy = model.score(X_test, y_test)

print("\n🎯 Model Accuracy:", accuracy)

# Save model
joblib.dump(model, "cry_model.pkl")

print("💾 Model saved as cry_model.pkl")