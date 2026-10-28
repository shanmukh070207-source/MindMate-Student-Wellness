"""Home page, dashboard, and the login-protected chart images."""
import logging
import sqlite3
from datetime import date

from flask import Blueprint, abort, render_template, send_file

import charts
from database.db import get_db
from routes.auth_routes import current_user_id, login_required

bp = Blueprint("main", __name__)
log = logging.getLogger(__name__)


@bp.route("/")
def index():
    return render_template("index.html")


@bp.route("/dashboard")
@login_required
def dashboard():
    user_id = current_user_id()
    db = get_db()
    today = date.today().isoformat()
    try:
        counts = charts.summary_counts(db, user_id)
        upcoming = db.execute(
            "SELECT id, title, subject, due_date FROM study_tasks "
            "WHERE user_id = ? AND status = 'pending' ORDER BY due_date ASC LIMIT 5",
            (user_id,),
        ).fetchall()
        recent_moods = db.execute(
            "SELECT mood, created_at FROM mood_entries WHERE user_id = ? "
            "ORDER BY created_at DESC, id DESC LIMIT 5",
            (user_id,),
        ).fetchall()
    except sqlite3.Error:
        log.exception("Dashboard query failed")
        counts = {"mood_count": 0, "pending": 0, "completed": 0, "overdue": 0, "journal_count": 0}
        upcoming, recent_moods = [], []

    # Only ask for chart images when there is real data behind them.
    show_mood_charts = counts["mood_count"] > 0
    show_task_chart = (counts["pending"] + counts["completed"]) > 0
    return render_template(
        "dashboard.html",
        counts=counts,
        upcoming=upcoming,
        recent_moods=recent_moods,
        today=today,
        show_mood_charts=show_mood_charts,
        show_task_chart=show_task_chart,
    )


@bp.route("/charts/<kind>.png")
@login_required
def chart_image(kind):
    """Draw a chart for the logged-in user only, and return it as a PNG."""
    image = charts.build_chart(kind, get_db(), current_user_id())
    if image is None:
        abort(404)
    response = send_file(image, mimetype="image/png")
    response.headers["Cache-Control"] = "no-store"
    return response
