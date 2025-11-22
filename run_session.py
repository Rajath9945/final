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
        print("Invalid input. Using default 1 minute.")
        duration_minutes = 1.0

    duration_seconds = duration_minutes * 60
    session_id = create_session_id()
    print(f"\nStarting session: {session_id}")
    print("Press CTRL + C to stop early.\n")

    emotion_counts = init_emotion_counts()
    total_faces_analyzed = 0
    total_frames = 0

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not access camera.")
        return

    yolo_model = YOLO("yolov8n.pt")  # auto-downloads on first run

    start_time = time.time()
    last_analysis_time = 0.0
    analysis_interval = 0.8

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to read camera frame.")
                break

            total_frames += 1
            current_time = time.time()

            if current_time - last_analysis_time >= analysis_interval:
                last_analysis_time = current_time
                try:
                    results = DeepFace.analyze(
                        frame,
                        actions=["emotion"],
                        enforce_detection=False
                    )

                    if isinstance(results, dict):
                        results = [results]

                    for r in results:
                        dominant = r.get("dominant_emotion", "").lower()

                        if dominant in ["happy", "surprise"]:
                            label = "laughing"
                        elif dominant in ["neutral"]:
                            label = "focused"
                        elif dominant in ["angry", "disgust", "fear"]:
                            label = "bored"
                        elif dominant == "sad":
                            label = "sad"
                        else:
                            label = None

                        if label is not None:
                            emotion_counts[label] += 1
                            total_faces_analyzed += 1

                except Exception as e:
                    print("DeepFace error:", e)

                phone_pred = yolo_model(frame, verbose=False)[0]
                phone_detected = False

                for box in phone_pred.boxes:
                    cls = int(box.cls[0])
                    label = phone_pred.names[cls]
                    if label in ["cell phone", "phone"]:
                        phone_detected = True
                        break

                if phone_detected:
                    emotion_counts["using_phone"] += 1
                    total_faces_analyzed += 1

            if current_time - start_time >= duration_seconds:
                print("Session completed.")
                break

    except KeyboardInterrupt:
        print("Session ended manually.")

    finally:
        cap.release()

    summary_path = save_session_summary(
        session_id=session_id,
        duration_minutes=duration_minutes,
        emotion_counts=emotion_counts,
        total_faces_analyzed=total_faces_analyzed,
        total_frames=total_frames
    )

    print("\n=== SESSION SUMMARY ===")
    print("Session ID:", session_id)
    print("Saved to:", summary_path)
    print("Total frames:", total_frames)
    print("Faces analyzed:", total_faces_analyzed)
    print("Emotion counts:", emotion_counts)

    print("\nRun: python app.py")
    print("Open: http://127.0.0.1:5000/")

if __name__ == "__main__":
    main()
