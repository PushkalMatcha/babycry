# utils.py

import cv2
from datetime import datetime
from firebase_config import send_event

def create_event(event_type):
    return {
        "type": event_type,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def save_snapshot(frame):
    filename = f"snapshot_{datetime.now().strftime('%H%M%S')}.jpg"
    cv2.imwrite(filename, frame)
    return filename

def log_event(event_type, frame=None):
    event = create_event(event_type)

    if frame is not None:
        filename = save_snapshot(frame)
        event["image"] = filename

    send_event(event)
    print("📡 Event sent to Firebase:", event)