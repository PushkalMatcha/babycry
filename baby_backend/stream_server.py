# stream_server.py

from flask import Flask, Response
from flask_cors import CORS
import cv2
import time
import os
import threading

from person_detection import detect_person
from audio_detection import detect_sound_background
from firebase_config import get_control_status, get_safe_zone
from utils import log_event

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests from the React dashboard

cap = cv2.VideoCapture(0)

# ── Video state ──────────────────────────────────────────────
frame_count = 0
last_alert_time = 0
outside_counter = 0
prev_position = None
last_frame = None

# ── Audio state ──────────────────────────────────────────────
audio_running = False
last_audio_time = 0
AUDIO_INTERVAL = 5   # seconds between audio checks
cry_count = 0
audio_lock = threading.Lock()


def save_snapshot(frame):
    if not os.path.exists("snapshots"):
        os.makedirs("snapshots")
    filename = f"snapshots/{int(time.time())}.jpg"
    cv2.imwrite(filename, frame)


# ── Cry callback (called from audio thread) ──────────────────
def cry_alert(detected):
    global cry_count
    with audio_lock:
        if detected:
            cry_count += 1
        else:
            cry_count = 0

        if cry_count >= 2:
            print("[cry] CONFIRMED CRY ALERT!")
            log_event("cry_detected")
            cry_count = 0


# ── Audio background thread launcher ────────────────────────
def maybe_start_audio():
    """Start a one-shot audio check on a background thread if not already running."""
    global audio_running, last_audio_time

    with audio_lock:
        if audio_running:
            return
        if time.time() - last_audio_time < AUDIO_INTERVAL:
            return
        audio_running = True
        last_audio_time = time.time()

    def run_audio():
        global audio_running
        try:
            detect_sound_background(cry_alert)()
        finally:
            with audio_lock:
                audio_running = False

    threading.Thread(target=run_audio, daemon=True).start()


# ── MJPEG frame generator ────────────────────────────────────
def generate_frames():
    global frame_count, last_alert_time, outside_counter, prev_position, last_frame

    while True:
        success, frame = cap.read()
        if not success:
            break

        # 🔥 LOWER RESOLUTION (LESS LAG)
        frame = cv2.resize(frame, (480, 360))
        h, w = frame.shape[:2]

        status = get_control_status()

        # 🛑 STOP MODE
        if status != "on":
            outside_counter = 0
            prev_position = None
            cv2.putText(frame, "Monitoring OFF", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            _, buffer = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            continue

        # ⚡ FRAME SKIP (SMOOTH)
        frame_count += 1
        if frame_count % 2 != 0:
            if last_frame is not None:
                _, buffer = cv2.imencode('.jpg', last_frame)
            else:
                _, buffer = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            continue

        # 👶 PERSON DETECTION
        person_detected, position, frame = detect_person(frame)

        # 📦 SAFE ZONE
        zone = get_safe_zone()
        if zone:
            zone_x1 = int(zone["x1"] * w)
            zone_y1 = int(zone["y1"] * h)
            zone_x2 = int(zone["x2"] * w)
            zone_y2 = int(zone["y2"] * h)
        else:
            zone_x1, zone_y1 = int(w * 0.3), int(h * 0.3)
            zone_x2, zone_y2 = int(w * 0.7), int(h * 0.7)

        cv2.rectangle(frame, (zone_x1, zone_y1), (zone_x2, zone_y2), (255, 0, 0), 2)

        # 🚨 STABLE MOVEMENT DETECTION
        if person_detected and position:
            x, y = position

            # 🔥 SMOOTH POSITION
            if prev_position:
                x = int((x + prev_position[0]) / 2)
                y = int((y + prev_position[1]) / 2)

            prev_position = (x, y)
            margin = 50

            inside_zone = (
                zone_x1 + margin < x < zone_x2 - margin and
                zone_y1 + margin < y < zone_y2 - margin
            )

            if not inside_zone:
                outside_counter += 1
            else:
                outside_counter = 0

            if outside_counter > 5:
                if time.time() - last_alert_time > 3:
                    print("[video] Baby moved!")
                    log_event("baby_moved")
                    save_snapshot(frame)
                    last_alert_time = time.time()
                    outside_counter = 0

            # 🎧 TRIGGER AUDIO CHECK (only when baby is visible)
            maybe_start_audio()

        # 🔥 SAVE LAST FRAME (ANTI-FLICKER)
        last_frame = frame.copy()

        _, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')


@app.route('/video')
def video():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)