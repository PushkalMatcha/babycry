# person_detection.py

import cv2
from config import PERSON_CONFIDENCE

# Load pretrained MobileNet SSD model
net = cv2.dnn.readNetFromCaffe(
    "deploy.prototxt",
    "mobilenet_iter_73000.caffemodel"
)

# Class labels (must match model exactly)
CLASSES = [
    "background", "aeroplane", "bicycle", "bird", "boat",
    "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
    "dog", "horse", "motorbike", "person"
]


def detect_person(frame):
    (h, w) = frame.shape[:2]

    # Preprocess image
    blob = cv2.dnn.blobFromImage(
        frame,
        scalefactor=0.007843,
        size=(300, 300),
        mean=127.5
    )

    net.setInput(blob)
    detections = net.forward()

    person_detected = False
    person_position = None  # (x, y)

    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]

        if confidence > PERSON_CONFIDENCE:
            idx = int(detections[0, 0, i, 1])

            # 🔥 SAFETY CHECK (prevents crash)
            if idx >= len(CLASSES):
                continue

            # Only detect person
            if CLASSES[idx] == "person":
                person_detected = True

                # Bounding box
                box = detections[0, 0, i, 3:7] * [w, h, w, h]
                (x1, y1, x2, y2) = box.astype("int")

                # Center point
                cx = (x1 + x2) // 2
                cy = (y1 + y2) // 2
                person_position = (cx, cy)

                # Draw bounding box
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                # Label
                cv2.putText(
                    frame,
                    "Baby Detected",
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2
                )

                # Draw center point
                cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)

    return person_detected, person_position, frame