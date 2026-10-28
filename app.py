"""MindMate - Student Mental Wellness Companion (Flask application factory)."""
import logging
import os
import secrets

from flask import Flask, abort, render_template, request, session

from config import Config
from database import db
from ml.predict import Classifier, ModelNotAvailableError

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("mindmate")


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)

    os.makedirs(os.path.dirname(app.config["DATABASE"]), exist_ok=True)

    # Database: create tables automatically if the file is new
    db.init_app(app)
    try:
        db.init_db(app.config["DATABASE"])
    except Exception:
        log.exception("Database initialization failed")

    # Load the trained model ONCE at startup. If it is missing we remember the
    # reason and the chat page shows a setup message (no fake predictions).
    app.extensions["classifier"] = None
    app.extensions["classifier_error"] = None
    try:
        app.extensions["classifier"] = Classifier.load(app.config["MODEL_PATH"])
        log.info("Chat model loaded")
    except ModelNotAvailableError as exc:
        app.extensions["classifier_error"] = str(exc)
        log.warning("Chat model unavailable: %s", exc)

    # ---- Simple CSRF protection for every POST request ----
    @app.before_request
    def csrf_protect():
        if "csrf_token" not in session:
            session["csrf_token"] = secrets.token_hex(16)
        if request.method == "POST" and not app.config.get("TESTING_SKIP_CSRF"):
            sent = request.form.get("csrf_token") or request.headers.get("X-CSRF-Token")
            if not sent or not secrets.compare_digest(sent, session["csrf_token"]):
                abort(400)

    @app.context_processor
    def inject_globals():
        return {
            "csrf_token": session.get("csrf_token", ""),
            "current_username": session.get("username"),
        }

    @app.after_request
    def security_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "same-origin")
        return response

    # ---- Blueprints ----
    from routes.activity_routes import bp as activity_bp
    from routes.auth_routes import bp as auth_bp
    from routes.chat_routes import bp as chat_bp
    from routes.main_routes import bp as main_bp
    from routes.mood_routes import bp as mood_bp
    from routes.planner_routes import bp as planner_bp
    from routes.resource_routes import bp as resource_bp

    for blueprint in (main_bp, auth_bp, chat_bp, planner_bp, mood_bp, activity_bp, resource_bp):
        app.register_blueprint(blueprint)

    # ---- Friendly error pages (never show stack traces) ----
    @app.errorhandler(404)
    def not_found(_e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(400)
    def bad_request(_e):
        return render_template("errors/400.html"), 400

    @app.errorhandler(413)
    def too_large(_e):
        return render_template("errors/400.html"), 413

    @app.errorhandler(500)
    def server_error(_e):
        return render_template("errors/500.html"), 500

    @app.errorhandler(Exception)
    def unexpected(error):
        from werkzeug.exceptions import HTTPException
        if isinstance(error, HTTPException):
            return error
        log.exception("Unhandled error")
        return render_template("errors/500.html"), 500

    return app


if __name__ == "__main__":
    # Debug mode is OFF by default. For local development only, you can run:
    #   set FLASK_DEBUG=1   (Windows)   /   export FLASK_DEBUG=1   (Linux/macOS)
    application = create_app()
    application.run(host="127.0.0.1", port=5000, debug=os.environ.get("FLASK_DEBUG") == "1")
