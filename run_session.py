import cv2
import time
import os
import uuid
from deepface import DeepFace
from ultralytics import YOLO
from emotion_utils import (
    create_session_id,
    init_emotion_counts,
    save_session_summary
)

# ===============================
# SESSION SETUP
# ===============================
duration_minutes = int(input("Enter monitoring duration in minutes: "))
session_id = create_session_id()

emotion_counts = init_emotion_counts()
start_time = time.time()
last_analysis = 0

total_faces_analyzed = 0
total_frames = 0

# ===============================
# NEW FEATURE: IMAGE STORAGE
# ===============================
EMOTIONS = ["focused", "laughing", "bored", "sad", "using_phone"]
BASE_DIR = os.path.join("static", "emotions", session_id)

for emo in EMOTIONS:
    os.makedirs(os.path.join(BASE_DIR, emo), exist_ok=True)

def save_emotion_image(frame, emotion):
    filename = f"{uuid.uuid4().hex}.jpg"
    path = os.path.join(BASE_DIR, emotion, filename)
    cv2.imwrite(path, frame)

# ===============================
# MODELS
# ===============================
cap = cv2.VideoCapture(0)
yolo = YOLO("yolov8n.pt")

print("Session started. Press Ctrl+C to stop.")

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        total_frames += 1
        current_time = time.time()

        # ===============================
        # EMOTION DETECTION (every 0.8s)
        # ===============================
        if current_time - last_analysis > 0.8:
            last_analysis = current_time
            try:
                results = DeepFace.analyze(
                    frame,
                    actions=["emotion"],
                    enforce_detection=False
                )

                dominant = results[0]["dominant_emotion"]

                if dominant in ["happy", "surprise"]:
                    mapped = "laughing"
                elif dominant == "neutral":
                    mapped = "focused"
                elif dominant in ["angry", "disgust", "fear"]:
                    mapped = "bored"
                else:
                    mapped = "sad"

                emotion_counts[mapped] += 1
                total_faces_analyzed += 1

                # ✅ NEW: save emotion image
                save_emotion_image(frame, mapped)

            except Exception:
                pass

        # ===============================
        # PHONE DETECTION (YOLO)
        # ===============================
        yolo_results = yolo(frame, verbose=False)

        for r in yolo_results:
            for box in r.boxes:
                cls = int(box.cls[0])
                label = yolo.names[cls]

                if label in ["cell phone", "phone"]:
                    emotion_counts["using_phone"] += 1

                    # ✅ NEW: save phone image
                    save_emotion_image(frame, "using_phone")

        if (current_time - start_time) / 60 >= duration_minutes:
            break

except KeyboardInterrupt:
    print("Session interrupted.")

cap.release()

# ===============================
# SAVE SESSION SUMMARY
# ===============================
save_session_summary(
    session_id=session_id,
    duration_minutes=duration_minutes,
    emotion_counts=emotion_counts,
    total_faces_analyzed=total_faces_analyzed,
    total_frames=total_frames
)

print("Session saved:", session_id)
print("Emotion counts:", emotion_counts)
