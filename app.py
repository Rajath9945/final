from flask import Flask, render_template, request, abort
from emotion_utils import load_all_sessions, load_session

app = Flask(__name__)


def compute_suggestions(session):
    counts = session["emotion_counts"]

    focused = counts.get("focused", 0)
    laughing = counts.get("laughing", 0)
    bored = counts.get("bored", 0)
    sad = counts.get("sad", 0)
    phone = counts.get("using_phone", 0)

    total = max(focused + laughing + bored + sad + phone, 1)

    engaged = focused + laughing
    disengaged = bored + sad + phone

    engaged_ratio = engaged / total
    phone_ratio = phone / total

    suggestions = []

    if engaged_ratio >= 0.7:
        suggestions.append("Excellent engagement — keep going!")
    elif engaged_ratio >= 0.5:
        suggestions.append("Moderate engagement — add interaction activities.")
    else:
        suggestions.append("Low engagement — include visual aids or real-life examples.")

    if phone_ratio > 0.2:
        suggestions.append("High mobile phone usage detected. Encourage students to focus.")

    return suggestions, {
        "engaged_ratio": round(engaged_ratio, 2),
        "disengaged_ratio": round(disengaged, 2),
        "phone_ratio": round(phone_ratio, 2),
    }


@app.route("/")
def home():
    sessions = load_all_sessions()
    sessions_sorted = sorted(sessions, key=lambda x: x["saved_at"], reverse=True)
    return render_template("base.html", sessions=sessions_sorted)


@app.route("/session/<session_id>")
def dashboard(session_id):
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
        stats=stats,
        suggestions=suggestions,
        session_list=load_all_sessions(),
    )


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
        s1_vals=[s1["emotion_counts"].get(lbl, 0) for lbl in labels],
        s2_vals=[s2["emotion_counts"].get(lbl, 0) for lbl in labels],
    )


if __name__ == "__main__":
    app.run(debug=True)
