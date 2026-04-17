# main.py

import cv2
import threading
import time
from person_detection import detect_person
from audio_detection import detect_sound_background
from utils import log_event
from config import CAMERA_INDEX
from firebase_config import get_control_status  # 🔥 NEW

def main():
    cap = cv2.VideoCapture(CAMERA_INDEX)

    if not cap.isOpened():
        print("❌ Camera not working")
        return

    audio_running = False
    last_audio_time = 0
    AUDIO_INTERVAL = 5

    last_no_baby_log = 0
    cry_count = 0

    def cry_alert(detected):
        nonlocal cry_count

        if detected:
            cry_count += 1
        else:
            cry_count = 0

        if cry_count >= 2:
            print("🚨 CONFIRMED CRY ALERT!")
            log_event("cry_detected")
            cry_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # 🔥 REMOTE CONTROL CHECK
        status = get_control_status()

        if status != "on":
            cv2.putText(frame, "Monitoring OFF", (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            cv2.imshow("Smart Baby Monitor", frame)

            if cv2.waitKey(1) == 27:
                break

            time.sleep(0.1)
            continue

        # 👶 Person detection
        person_detected, position, frame = detect_person(frame)

        frame_height, frame_width = frame.shape[:2]

        # 🟦 Safe zone
        zone_x1 = int(frame_width * 0.3)
        zone_x2 = int(frame_width * 0.7)
        zone_y1 = int(frame_height * 0.3)
        zone_y2 = int(frame_height * 0.7)

        cv2.rectangle(frame, (zone_x1, zone_y1), (zone_x2, zone_y2), (255, 0, 0), 2)

        if person_detected and position:
            x, y = position

            if not (zone_x1 < x < zone_x2 and zone_y1 < y < zone_y2):
                print("🚨 Baby moved out of safe zone!")
                log_event("baby_moved")

            # 🎧 Audio detection
            if not audio_running and (time.time() - last_audio_time > AUDIO_INTERVAL):
                audio_running = True
                last_audio_time = time.time()

                def run_audio():
                    nonlocal audio_running
                    detect_sound_background(cry_alert)()
                    audio_running = False

                threading.Thread(target=run_audio).start()

        else:
            if time.time() - last_no_baby_log > 10:
                print("❌ No Baby Detected")
                log_event("no_baby")
                last_no_baby_log = time.time()

        cv2.imshow("Smart Baby Monitor", frame)

        if cv2.waitKey(1) == 27:
            break

        time.sleep(0.02)

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()