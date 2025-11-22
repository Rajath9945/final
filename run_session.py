import time
from datetime import datetime
import cv2
from deepface import DeepFace
from ultralytics import YOLO

from emotion_utils import (
    create_session_id,
    init_emotion_counts,
    save_session_summary
)

def main():
    try:
        duration_minutes = float(input("Enter monitoring duration in minutes (e.g., 1.5): "))
    except ValueError:
        duration_minutes = 1.0

    duration_seconds = duration_minutes * 60
    session_id = create_session_id()
    print(f"\nStarting session: {session_id}\n")

    emotion_counts = init_emotion_counts()
    total_faces_analyzed = 0
    total_frames = 0

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Camera not accessible")
        return

    yolo_model = YOLO("yolov8n.pt")

    start_time = time.time()
    last_time = 0
    interval = 0.8

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            total_frames += 1
            now = time.time()

            if now - last_time >= interval:
                last_time = now
                try:
                    results = DeepFace.analyze(
                        frame, actions=["emotion"], enforce_detection=False
                    )
                    if isinstance(results, dict):
                        results = [results]

                    for r in results:
                        emo = r.get("dominant_emotion", "").lower()

                        if emo in ["happy", "surprise"]:
                            label = "laughing"
                        elif emo in ["neutral"]:
                            label = "focused"
                        elif emo in ["angry", "disgust", "fear"]:
                            label = "bored"
                        elif emo == "sad":
                            label = "sad"
                        else:
                            label = None

                        if label:
                            emotion_counts[label] += 1
                            total_faces_analyzed += 1

                except Exception as e:
                    print("DeepFace:", e)

                phone_pred = yolo_model(frame, verbose=False)[0]
                phone = False
                for box in phone_pred.boxes:
                    cls = int(box.cls[0])
                    label = phone_pred.names[cls]
                    if label in ["cell phone", "phone"]:
                        phone = True
                        break

                if phone:
                    emotion_counts["using_phone"] += 1
                    total_faces_analyzed += 1

            if now - start_time >= duration_seconds:
                break

    except KeyboardInterrupt:
        print("Stopped manually")

    finally:
        cap.release()

    path = save_session_summary(
        session_id,
        duration_minutes,
        emotion_counts,
        total_faces_analyzed,
        total_frames
    )

    print("\n=== SUMMARY ===")
    print("Saved:", path)
    print("Counts:", emotion_counts)
    print("\nRun: python app.py")
    print("Visit: http://127.0.0.1:5000/")

if __name__ == "__main__":
    main()
