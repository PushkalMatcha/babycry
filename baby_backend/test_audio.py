import sounddevice as sd
from config import SAMPLE_RATE, DURATION, AUDIO_DEVICE

sd.default.device = (AUDIO_DEVICE, None)

print("Recording...")

audio = sd.rec(int(DURATION * SAMPLE_RATE),
               samplerate=SAMPLE_RATE,
               channels=1)

sd.wait()

print("✅ Audio working!")