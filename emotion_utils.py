import json
import os
from datetime import datetime
from typing import Dict

EMOTION_LABELS = ["focused", "laughing", "bored", "sad", "using_phone"]

SESSIONS_DIR = os.path.join("data", "sessions")
os.makedirs(SESSIONS_DIR, exist_ok=True)


def create_session_id() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def init_emotion_counts() -> Dict[str, int]:
    return {e: 0 for e in EMOTION_LABELS}


def save_session_summary(session_id, duration_minutes, emotion_counts, total_faces_analyzed, total_frames):
    data = {
        "session_id": session_id,
        "duration_minutes": duration_minutes,
        "total_frames": total_frames,
        "total_faces_analyzed": total_faces_analyzed,
        "emotion_counts": emotion_counts,
        "total_emotion_samples": sum(emotion_counts.values()),
        "saved_at": datetime.now().isoformat()
    }

    path = os.path.join(SESSIONS_DIR, f"session_{session_id}.json")
    with open(path, "w") as f:
        json.dump(data, f, indent=4)
    return path


def load_all_sessions():
    sessions = []
    for f in os.listdir(SESSIONS_DIR):
        if f.endswith(".json"):
            with open(os.path.join(SESSIONS_DIR, f)) as fp:
                sessions.append(json.load(fp))
    return sessions


def load_session(session_id: str):
    path = os.path.join(SESSIONS_DIR, f"session_{session_id}.json")
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)
