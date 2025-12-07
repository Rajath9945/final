from flask import Flask, render_template, request, abort
from emotion_utils import (
    load_all_sessions,
    load_session,
    load_emotion_images
)

app = Flask(__name__)

# ==============================
# SUGGESTIONS & METRICS
# ==============================
def compute_suggestions(session):
    counts = session["emotion_counts"]

    focused = counts.get("focused", 0)
    laughing = counts.get("laughing", 0)
    bored = counts.get("bored", 0)
    sad = counts.get("sad", 0)
    phone = counts.get("using_phone", 0)

    total = max(focused + laughing + bored + sad + phone, 1)

    engaged = focused + laughing
    engaged_ratio = engaged / total
    phone_ratio = phone / total

    suggestions = []

    if engaged_ratio >= 0.7:
        suggestions.append("Excellent engagement observed throughout the session.")
    elif engaged_ratio >= 0.5:
        suggestions.append("Moderate engagement. Consider adding interactive activities.")
    else:
        suggestions.append("Low engagement detected. Use visual aids and real-life examples.")

    if phone_ratio > 0.2:
        suggestions.append("High mobile phone usage detected. Attention control is recommended.")

    return suggestions, {
        "engaged_ratio": round(engaged_ratio, 2),
        "phone_ratio": round(phone_ratio, 2)
    }


# ==============================
# HOME – LIST ALL SESSIONS
# ==============================
@app.route("/")
def home():
    sessions = load_all_sessions()
    sessions_sorted = sorted(
        sessions,
        key=lambda x: x["saved_at"],
        reverse=True
    )
    return render_template("base.html", sessions=sessions_sorted)


# ==============================
# SESSION DASHBOARD
# ==============================
@app.route("/session/<session_id>")
def dashboard(session_id):
    session = load_session(session_id)
    if not session:
        abort(404)

    labels = list(session["emotion_counts"].keys())
    values = list(session["emotion_counts"].values())

    suggestions, stats = compute_suggestions(session)
    images = load_emotion_images(session_id)

    return render_template(
        "dashboard.html",
        session=session,
        labels=labels,
        values=values,
        stats=stats,
        suggestions=suggestions,
        images=images,
        session_list=load_all_sessions()
    )


# ==============================
# COMPARE TWO SESSIONS
# ==============================
@app.route("/compare", methods=["POST"])
def compare():
    s1 = load_session(request.form.get("current_session"))
    s2 = load_session(request.form.get("compare_session"))

    if not s1 or not s2:
        abort(404)

    labels = list(s1["emotion_counts"].keys())

    return render_template(
        "compare.html",
        labels=labels,
        s1=s1,
        s2=s2,
        s1_vals=[s1["emotion_counts"].get(l, 0) for l in labels],
        s2_vals=[s2["emotion_counts"].get(l, 0) for l in labels]
    )


# ==============================
# ✅ ANALYTICS – COMPARE ALL SESSIONS
# ==============================
@app.route("/analytics")
def analytics():
    sessions = load_all_sessions()

    session_ids = []
    engagement_scores = []
    phone_scores = []

    for s in sessions:
        counts = s["emotion_counts"]

        focused = counts.get("focused", 0)
        laughing = counts.get("laughing", 0)
        bored = counts.get("bored", 0)
        sad = counts.get("sad", 0)
        phone = counts.get("using_phone", 0)

        total = max(focused + laughing + bored + sad + phone, 1)
        engaged = focused + laughing

        engagement = round((engaged / total) * 100, 2)
        phone_ratio = round((phone / total) * 100, 2)

        session_ids.append(s["session_id"])
        engagement_scores.append(engagement)
        phone_scores.append(phone_ratio)

    # ✅ CLASS AVERAGE
    avg_engagement = round(sum(engagement_scores) / max(len(engagement_scores), 1), 2)

    # ✅ CLASS GRADE
    if avg_engagement >= 80:
        grade = "A (Excellent)"
    elif avg_engagement >= 65:
        grade = "B (Good)"
    elif avg_engagement >= 50:
        grade = "C (Average)"
    else:
        grade = "D (Poor)"

    return render_template(
        "analytics.html",
        session_ids=session_ids,
        engagement_scores=engagement_scores,
        phone_scores=phone_scores,
        avg_engagement=avg_engagement,
        grade=grade,
        total_sessions=len(session_ids)
    )
@app.route("/founders")
def founders():
    return render_template("founders.html")


# ==============================
# RUN APP
# ==============================
if __name__ == "__main__":
    app.run(debug=True)
