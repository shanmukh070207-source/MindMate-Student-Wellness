"""Mood tracker: save, list and delete mood entries."""
import logging
import sqlite3

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from database.db import get_db
from routes.auth_routes import current_user_id, login_required

bp = Blueprint("mood", __name__, url_prefix="/mood")
log = logging.getLogger(__name__)

MOODS = ["Very Good", "Good", "Okay", "Stressed", "Low"]
MAX_NOTE = 500


def validate_mood_form(form):
    mood = (form.get("mood") or "").strip()
    note = (form.get("note") or "").strip()
    errors = []
    if mood not in MOODS:
        errors.append("Please choose one of the mood options.")
    if len(note) > MAX_NOTE:
        errors.append(f"The note must be at most {MAX_NOTE} characters.")
    return {"mood": mood, "note": note}, errors


@bp.route("/", methods=["GET"])
@login_required
def mood_tracker():
    try:
        entries = get_db().execute(
            "SELECT id, mood, note, created_at FROM mood_entries WHERE user_id = ? "
            "ORDER BY created_at DESC, id DESC LIMIT 100",
            (current_user_id(),),
        ).fetchall()
    except sqlite3.Error:
        log.exception("Could not load mood entries")
        entries = []
        flash("Sorry, your mood history could not be loaded.", "error")
    return render_template("mood_tracker.html", entries=entries, moods=MOODS)


@bp.route("/add", methods=["POST"])
@login_required
def add_mood():
    values, errors = validate_mood_form(request.form)
    if errors:
        for message in errors:
            flash(message, "error")
        return redirect(url_for("mood.mood_tracker"))
    try:
        db = get_db()
        db.execute(
            "INSERT INTO mood_entries (user_id, mood, note) VALUES (?, ?, ?)",
            (current_user_id(), values["mood"], values["note"]),
        )
        db.commit()
        flash("Mood saved.", "success")
    except sqlite3.Error:
        log.exception("Could not save mood")
        flash("Sorry, your mood could not be saved.", "error")
    return redirect(url_for("mood.mood_tracker"))


@bp.route("/<int:entry_id>/delete", methods=["POST"])
@login_required
def delete_mood(entry_id):
    db = get_db()
    row = db.execute(
        "SELECT id FROM mood_entries WHERE id = ? AND user_id = ?", (entry_id, current_user_id())
    ).fetchone()
    if row is None:
        abort(404)
    try:
        db.execute("DELETE FROM mood_entries WHERE id = ? AND user_id = ?", (entry_id, current_user_id()))
        db.commit()
        flash("Mood entry deleted.", "success")
    except sqlite3.Error:
        log.exception("Could not delete mood")
        flash("Sorry, the entry could not be deleted.", "error")
    return redirect(url_for("mood.mood_tracker"))
