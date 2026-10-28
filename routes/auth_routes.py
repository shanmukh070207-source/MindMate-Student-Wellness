"""Simple account system: register, log in, log out.

Passwords are stored as salted hashes (werkzeug). Every private page uses the
@login_required decorator, and every query filters by the logged-in user's id.
A production deployment would need additional security review (rate limiting,
HTTPS, password reset, etc.).
"""
import re
import sqlite3
from functools import wraps

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from database.db import get_db

bp = Blueprint("auth", __name__)

USERNAME_RE = re.compile(r"^[A-Za-z0-9_]{3,30}$")


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if session.get("user_id") is None:
            flash("Please log in to continue.", "info")
            return redirect(url_for("auth.login", next=request.path))
        return view(*args, **kwargs)
    return wrapped


def current_user_id():
    return session.get("user_id")


def _safe_next(target):
    """Only allow redirects to paths inside this site."""
    if target and target.startswith("/") and not target.startswith("//"):
        return target
    return None


@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""
        confirm = request.form.get("confirm") or ""
        error = None
        if not USERNAME_RE.match(username):
            error = "Username must be 3-30 characters: letters, numbers or underscore."
        elif len(password) < 8:
            error = "Password must be at least 8 characters."
        elif password != confirm:
            error = "The passwords do not match."
        if error is None:
            try:
                database = get_db()
                database.execute(
                    "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                database.commit()
                flash("Account created. You can log in now.", "success")
                return redirect(url_for("auth.login"))
            except sqlite3.IntegrityError:
                error = "That username is already taken."
            except sqlite3.Error:
                error = "We could not create your account. Please try again."
        flash(error, "error")
    return render_template("register.html")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""
        try:
            user = get_db().execute(
                "SELECT id, username, password_hash FROM users WHERE username = ?", (username,)
            ).fetchone()
        except sqlite3.Error:
            user = None
        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            flash(f"Welcome back, {user['username']}!", "success")
            return redirect(_safe_next(request.args.get("next")) or url_for("main.dashboard"))
        flash("Incorrect username or password.", "error")
    return render_template("login.html")


@bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.index"))
