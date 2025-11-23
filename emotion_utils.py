import os
import json
from datetime import datetime
from typing import Dict

EMOTION_LABELS = ["focused", "laughing", "bored", "sad", "using_phone"]

SESSIONS_DIR = os.path.join("data", "sessions")
os.makedirs(SESSIONS_DIR, exist_ok=True)


def create_session_id() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def init_emotion_counts() -> Dict[str, int]:
    return {label: 0 for label in EMOTION_LABELS}


def save_session_summary(
    session_id: str,
    duration_minutes: float,
    emotion_counts: Dict[str, int],
    total_faces_analyzed: int,
    total_frames: int,
):
    data = {
        "session_id": session_id,
        "duration_minutes": duration_minutes,
        "total_faces_analyzed": total_faces_analyzed,
        "total_frames": total_frames,
        "emotion_counts": emotion_counts,
        "total_emotion_samples": sum(emotion_counts.values()),
        "saved_at": datetime.now().isoformat(),
    }

    file_path = os.path.join(SESSIONS_DIR, f"session_{session_id}.json")
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)


def load_all_sessions():
    sessions = []
    if not os.path.exists(SESSIONS_DIR):
        return sessions

    for fname in os.listdir(SESSIONS_DIR):
        if fname.endswith(".json"):
            with open(os.path.join(SESSIONS_DIR, fname), "r") as f:
                sessions.append(json.load(f))
    return sessions


def load_session(session_id: str):
    file_path = os.path.join(SESSIONS_DIR, f"session_{session_id}.json")
    if not os.path.exists(file_path):
        return None
    with open(file_path, "r") as f:
        return json.load(f)
