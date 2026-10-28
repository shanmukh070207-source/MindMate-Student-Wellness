"""Dashboard data and charts: Pandas processes the data, Matplotlib draws it.

Charts are drawn on the server and returned as PNG bytes by a login-protected
route (see routes/main_routes.py). Nothing is written to a public folder, and
every query filters by the logged-in user's id, so one user's data never ends
up in another user's chart.
"""
import io
import logging
from datetime import date

import matplotlib

matplotlib.use("Agg")  # no display needed on the server
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

log = logging.getLogger(__name__)

MOOD_SCORES = {"Very Good": 5, "Good": 4, "Okay": 3, "Stressed": 2, "Low": 1}
SCORE_LABELS = {5: "Very Good", 4: "Good", 3: "Okay", 2: "Stressed", 1: "Low"}
MOOD_COLORS = {"Very Good": "#4f9d8a", "Good": "#8cc4a8", "Okay": "#c9c9c9", "Stressed": "#e6b27a", "Low": "#8aa0c8"}


def load_moods(db, user_id):
    rows = db.execute(
        "SELECT mood, created_at FROM mood_entries WHERE user_id = ? ORDER BY created_at", (user_id,)
    ).fetchall()
    df = pd.DataFrame([dict(r) for r in rows], columns=["mood", "created_at"])
    if not df.empty:
        df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
        df = df.dropna(subset=["created_at"])
        df["score"] = df["mood"].map(MOOD_SCORES)
    return df


def load_tasks(db, user_id):
    rows = db.execute(
        "SELECT status, due_date FROM study_tasks WHERE user_id = ?", (user_id,)
    ).fetchall()
    return pd.DataFrame([dict(r) for r in rows], columns=["status", "due_date"])


def summary_counts(db, user_id):
    """Plain numbers for the dashboard cards, taken from the database."""
    today = date.today().isoformat()
    one = lambda sql, args: db.execute(sql, args).fetchone()[0]  # noqa: E731
    return {
        "mood_count": one("SELECT COUNT(*) FROM mood_entries WHERE user_id = ?", (user_id,)),
        "pending": one("SELECT COUNT(*) FROM study_tasks WHERE user_id = ? AND status = 'pending'", (user_id,)),
        "completed": one("SELECT COUNT(*) FROM study_tasks WHERE user_id = ? AND status = 'completed'", (user_id,)),
        "overdue": one(
            "SELECT COUNT(*) FROM study_tasks WHERE user_id = ? AND status = 'pending' AND due_date < ?",
            (user_id, today)),
        "journal_count": one("SELECT COUNT(*) FROM journal_entries WHERE user_id = ?", (user_id,)),
    }


def _png(fig):
    """Render a figure to PNG bytes."""
    buffer = io.BytesIO()
    fig.tight_layout()
    fig.savefig(buffer, format="png", dpi=110)
    plt.close(fig)
    buffer.seek(0)
    return buffer


def mood_trend_chart(db, user_id):
    """Line chart of mood score over time. Returns PNG bytes (BytesIO) or None when there is no data."""
    df = load_moods(db, user_id)
    if df.empty:
        return None
    df = df.tail(30)
    fig, ax = plt.subplots(figsize=(7, 3.2))
    ax.plot(df["created_at"], df["score"], marker="o", color="#4f7cac", linewidth=2)
    ax.set_ylim(0.5, 5.5)
    ax.set_yticks(list(SCORE_LABELS.keys()))
    ax.set_yticklabels([SCORE_LABELS[k] for k in SCORE_LABELS])
    ax.set_title("Your mood over time (last 30 entries)")
    ax.set_xlabel("Date")
    ax.grid(alpha=0.25)
    fig.autofmt_xdate()
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%d %b"))
    return _png(fig)


def mood_distribution_chart(db, user_id):
    """Bar chart: how many times each mood was recorded."""
    df = load_moods(db, user_id)
    if df.empty:
        return None
    counts = df["mood"].value_counts().reindex(list(MOOD_SCORES.keys()), fill_value=0)
    fig, ax = plt.subplots(figsize=(4.2, 3.2))
    ax.bar(counts.index, counts.values, color=[MOOD_COLORS[m] for m in counts.index])
    ax.set_title("Moods recorded")
    ax.set_ylabel("Entries")
    ax.yaxis.get_major_locator().set_params(integer=True)
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
    return _png(fig)


def task_status_chart(db, user_id):
    """Bar chart of completed / pending / overdue tasks."""
    df = load_tasks(db, user_id)
    if df.empty:
        return None
    today = date.today().isoformat()
    pending = df[df["status"] == "pending"]
    overdue = int((pending["due_date"] < today).sum())
    values = {
        "Completed": int((df["status"] == "completed").sum()),
        "Pending": int(len(pending)) - overdue,
        "Overdue": overdue,
    }
    fig, ax = plt.subplots(figsize=(4.2, 3.2))
    ax.bar(values.keys(), values.values(), color=["#4f9d8a", "#7fa8d1", "#d98c8c"])
    ax.set_title("Study tasks")
    ax.set_ylabel("Tasks")
    ax.yaxis.get_major_locator().set_params(integer=True)
    return _png(fig)


CHART_BUILDERS = {
    "mood_trend": mood_trend_chart,
    "mood_dist": mood_distribution_chart,
    "tasks": task_status_chart,
}


def build_chart(kind, db, user_id):
    """Return PNG bytes for one chart, or None if there is no data or it failed."""
    builder = CHART_BUILDERS.get(kind)
    if builder is None:
        return None
    try:
        return builder(db, user_id)
    except Exception:
        log.exception("Chart '%s' could not be created", kind)
        return None
