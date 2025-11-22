# app.py

from flask import Flask, render_template, abort
from emotion_utils import load_all_sessions, load_session, EMOTION_LABELS

app = Flask(__name__)


def compute_suggestions(session):
    counts = session["emotion_counts"]
    total = session["total_emotion_samples"] or 1

    # Simple grouping:
    engaged = counts.get("happy", 0) + counts.get("surprise", 0) + counts.get("neutral", 0)
    disengaged = counts.get("sad", 0) + counts.get("angry", 0) + counts.get("disgust", 0) + counts.get("fear", 0)

    engaged_ratio = engaged / total
    disengaged_ratio = disengaged / total

    suggestions = []

    if engaged_ratio >= 0.6:
        suggestions.append("Overall engagement is high. You can maintain the current teaching pace.")
    elif 0.4 <= engaged_ratio < 0.6:
        suggestions.append("Engagement is moderate. Consider adding short interactive questions or activities.")
    else:
        suggestions.append("Engagement appears low. Try using more real-life examples, group activities, or a short break.")

    if counts.get("sad", 0) > counts.get("happy", 0):
        suggestions.append("Many students look sad/bored. Check if the topic is too difficult or if the speed is too fast.")
    if counts.get("angry", 0) > 0:
        suggestions.append("Some frustration detected (angry emotion). Clarify tricky concepts and invite questions.")
    if counts.get("happy", 0) > 0:
        suggestions.append("There are happy/laughing moments – keep using humor and positive feedback.")
    if counts.get("neutral", 0) > 0 and engaged_ratio < 0.5:
        suggestions.append("Many neutral faces. You may need to increase interaction to convert neutral to engaged.")

    return suggestions, {
        "engaged_ratio": round(engaged_ratio, 2),
        "disengaged_ratio": round(disengaged_ratio, 2),
        "total": total,
    }


@app.route("/")
def home():
    sessions = load_all_sessions()
    # Sort newest first by saved_at if present
    sessions_sorted = sorted(
        sessions,
        key=lambda s: s.get("saved_at", ""),
        reverse=True
    )
    return render_template("base.html", sessions=sessions_sorted)


@app.route("/session/<session_id>")
def session_dashboard(session_id):
    session = load_session(session_id)
    if not session:
        abort(404)

    labels = list(session["emotion_counts"].keys())
    values = [session["emotion_counts"][l] for l in labels]

    suggestions, stats = compute_suggestions(session)

    return render_template(
        "dashboard.html",
        session=session,
        labels=labels,
        values=values,
        suggestions=suggestions,
        stats=stats,
    )


if __name__ == "__main__":
    # Debug=True for development
    app.run(debug=True)
