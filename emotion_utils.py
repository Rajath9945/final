import os
import json
from datetime import datetime

SESSION_DIR = "data/sessions"

os.makedirs(SESSION_DIR, exist_ok=True)

def create_session_id():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def init_emotion_counts():
    return {
        "focused": 0,
        "laughing": 0,
        "bored": 0,
        "sad": 0,
        "using_phone": 0
    }

def save_session_summary(session_id, duration_minutes, emotion_counts,
                         total_faces_analyzed, total_frames):

    data = {
        "session_id": session_id,
        "duration_minutes": duration_minutes,
        "emotion_counts": emotion_counts,
        "total_faces_analyzed": total_faces_analyzed,
        "total_frames": total_frames,
        "total_emotion_samples": sum(emotion_counts.values()),
        "saved_at": datetime.now().isoformat()
    }

    path = os.path.join(SESSION_DIR, f"session_{session_id}.json")
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def load_all_sessions():
    sessions = []
    for file in os.listdir(SESSION_DIR):
        if file.endswith(".json"):
            with open(os.path.join(SESSION_DIR, file)) as f:
                sessions.append(json.load(f))
    return sessions

def load_session(session_id):
    path = os.path.join(SESSION_DIR, f"session_{session_id}.json")
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)

# ===============================
# NEW FEATURE: LOAD EMOTION IMAGES
# ===============================
def load_emotion_images(session_id):
    base = os.path.join("static", "emotions", session_id)
    images = {}

    for emo in ["focused", "laughing", "bored", "sad", "using_phone"]:
        emo_dir = os.path.join(base, emo)
        if os.path.exists(emo_dir):
            images[emo] = [
                f"/static/emotions/{session_id}/{emo}/{img}"
                for img in os.listdir(emo_dir)
            ]
        else:
            images[emo] = []

    return images
