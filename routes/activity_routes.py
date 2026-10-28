"""Stress-relief activities and private journaling."""
import logging
import sqlite3

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from database.db import get_db
from routes.auth_routes import current_user_id, login_required

bp = Blueprint("activities", __name__)
log = logging.getLogger(__name__)

MAX_JOURNAL = 5000


@bp.route("/activities")
@login_required
def activities():
    return render_template("activities.html")


@bp.route("/journal", methods=["GET"])
@login_required
def journaling():
    try:
        entries = get_db().execute(
            "SELECT id, entry_text, created_at FROM journal_entries WHERE user_id = ? "
            "ORDER BY created_at DESC, id DESC LIMIT 100",
            (current_user_id(),),
        ).fetchall()
    except sqlite3.Error:
        log.exception("Could not load journal entries")
        entries = []
        flash("Sorry, your journal could not be loaded.", "error")
    return render_template("journaling.html", entries=entries, max_length=MAX_JOURNAL)


@bp.route("/journal/add", methods=["POST"])
@login_required
def add_journal():
    text = (request.form.get("entry_text") or "").strip()
    if not text:
        flash("Your journal entry is empty. Write something first, or just leave this page.", "error")
    elif len(text) > MAX_JOURNAL:
        flash(f"Journal entries can be at most {MAX_JOURNAL} characters.", "error")
    else:
        try:
            db = get_db()
            db.execute("INSERT INTO journal_entries (user_id, entry_text) VALUES (?, ?)",
                       (current_user_id(), text))
            db.commit()
            flash("Entry saved privately to your account.", "success")
        except sqlite3.Error:
            log.exception("Could not save journal entry")
            flash("Sorry, your entry could not be saved.", "error")
    return redirect(url_for("activities.journaling"))


@bp.route("/journal/<int:entry_id>/delete", methods=["POST"])
@login_required
def delete_journal(entry_id):
    db = get_db()
    row = db.execute("SELECT id FROM journal_entries WHERE id = ? AND user_id = ?",
                     (entry_id, current_user_id())).fetchone()
    if row is None:
        abort(404)
    try:
        db.execute("DELETE FROM journal_entries WHERE id = ? AND user_id = ?", (entry_id, current_user_id()))
        db.commit()
        flash("Journal entry deleted.", "success")
    except sqlite3.Error:
        log.exception("Could not delete journal entry")
        flash("Sorry, the entry could not be deleted.", "error")
    return redirect(url_for("activities.journaling"))
