"""Study planner: add, edit, complete, delete and list tasks.

The server validates everything. JavaScript only adds a delete confirmation.
Every query includes user_id, so a user cannot touch another user's task by
changing the id in the URL (they simply get a 404).
"""
import logging
import sqlite3
from datetime import date, datetime

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from database.db import get_db
from routes.auth_routes import current_user_id, login_required

bp = Blueprint("planner", __name__, url_prefix="/planner")
log = logging.getLogger(__name__)

MAX_TITLE = 100
MAX_SUBJECT = 50
MAX_DESCRIPTION = 500
VIEWS = ("all", "upcoming", "overdue", "completed")


def validate_task_form(form):
    """Return (clean_values, errors). Pure function so it is easy to test."""
    title = (form.get("title") or "").strip()
    subject = (form.get("subject") or "").strip()
    description = (form.get("description") or "").strip()
    due_raw = (form.get("due_date") or "").strip()
    errors = []

    if not title:
        errors.append("Please enter a task title.")
    elif len(title) > MAX_TITLE:
        errors.append(f"The title must be at most {MAX_TITLE} characters.")
    if len(subject) > MAX_SUBJECT:
        errors.append(f"The subject must be at most {MAX_SUBJECT} characters.")
    if len(description) > MAX_DESCRIPTION:
        errors.append(f"The description must be at most {MAX_DESCRIPTION} characters.")

    due_date = None
    if not due_raw:
        errors.append("Please choose a due date.")
    else:
        try:
            due_date = datetime.strptime(due_raw, "%Y-%m-%d").date().isoformat()
        except ValueError:
            errors.append("The due date is not a valid date.")

    return {"title": title, "subject": subject, "description": description, "due_date": due_date}, errors


def get_task_or_404(task_id):
    task = get_db().execute(
        "SELECT * FROM study_tasks WHERE id = ? AND user_id = ?", (task_id, current_user_id())
    ).fetchone()
    if task is None:
        abort(404)
    return task


@bp.route("/", methods=["GET"])
@login_required
def planner():
    view = request.args.get("view", "all")
    if view not in VIEWS:
        view = "all"
    order = "DESC" if request.args.get("order") == "desc" else "ASC"
    today = date.today().isoformat()

    sql = "SELECT * FROM study_tasks WHERE user_id = ?"
    args = [current_user_id()]
    if view == "upcoming":
        sql += " AND status = 'pending' AND due_date >= ?"
        args.append(today)
    elif view == "overdue":
        sql += " AND status = 'pending' AND due_date < ?"
        args.append(today)
    elif view == "completed":
        sql += " AND status = 'completed'"
    # 'order' is limited to two fixed words above, so this is safe.
    sql += f" ORDER BY due_date {order}, id ASC"

    try:
        tasks = get_db().execute(sql, args).fetchall()
    except sqlite3.Error:
        log.exception("Could not load tasks")
        tasks = []
        flash("Sorry, your tasks could not be loaded right now.", "error")
    return render_template("planner.html", tasks=tasks, view=view, order=order.lower(), today=today)


@bp.route("/add", methods=["POST"])
@login_required
def add_task():
    values, errors = validate_task_form(request.form)
    if errors:
        for message in errors:
            flash(message, "error")
        return redirect(url_for("planner.planner"))
    try:
        db = get_db()
        db.execute(
            "INSERT INTO study_tasks (user_id, title, description, subject, due_date) VALUES (?, ?, ?, ?, ?)",
            (current_user_id(), values["title"], values["description"], values["subject"], values["due_date"]),
        )
        db.commit()
        flash("Task added.", "success")
    except sqlite3.Error:
        log.exception("Could not add task")
        flash("Sorry, the task could not be saved.", "error")
    return redirect(url_for("planner.planner"))


@bp.route("/<int:task_id>/edit", methods=["GET", "POST"])
@login_required
def edit_task(task_id):
    task = get_task_or_404(task_id)
    if request.method == "POST":
        values, errors = validate_task_form(request.form)
        if errors:
            for message in errors:
                flash(message, "error")
            # show the form again with what the user typed
            task = {**dict(task), **{k: v for k, v in values.items() if v is not None},
                    "due_date": request.form.get("due_date", "")}
            return render_template("edit_task.html", task=task), 400
        try:
            db = get_db()
            db.execute(
                "UPDATE study_tasks SET title = ?, description = ?, subject = ?, due_date = ?, "
                "updated_at = datetime('now') WHERE id = ? AND user_id = ?",
                (values["title"], values["description"], values["subject"], values["due_date"],
                 task_id, current_user_id()),
            )
            db.commit()
            flash("Task updated.", "success")
        except sqlite3.Error:
            log.exception("Could not update task")
            flash("Sorry, the task could not be updated.", "error")
        return redirect(url_for("planner.planner"))
    return render_template("edit_task.html", task=task)


@bp.route("/<int:task_id>/toggle", methods=["POST"])
@login_required
def toggle_task(task_id):
    task = get_task_or_404(task_id)
    new_status = "pending" if task["status"] == "completed" else "completed"
    try:
        db = get_db()
        db.execute(
            "UPDATE study_tasks SET status = ?, updated_at = datetime('now') WHERE id = ? AND user_id = ?",
            (new_status, task_id, current_user_id()),
        )
        db.commit()
        flash("Task marked as completed." if new_status == "completed" else "Task moved back to pending.", "success")
    except sqlite3.Error:
        log.exception("Could not change task status")
        flash("Sorry, the task could not be updated.", "error")
    return redirect(request.referrer or url_for("planner.planner"))


@bp.route("/<int:task_id>/delete", methods=["POST"])
@login_required
def delete_task(task_id):
    get_task_or_404(task_id)
    try:
        db = get_db()
        db.execute("DELETE FROM study_tasks WHERE id = ? AND user_id = ?", (task_id, current_user_id()))
        db.commit()
        flash("Task deleted.", "success")
    except sqlite3.Error:
        log.exception("Could not delete task")
        flash("Sorry, the task could not be deleted.", "error")
    return redirect(url_for("planner.planner"))
