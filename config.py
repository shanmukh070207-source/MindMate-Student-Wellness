"""Application configuration.

The secret key is read from the MINDMATE_SECRET_KEY environment variable.
It is never stored in source code. If it is missing, a random key is
generated for this run only (sessions will reset when the server restarts).
"""
import os
import secrets

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("MINDMATE_SECRET_KEY") or secrets.token_hex(32)
    DATABASE = os.path.join(BASE_DIR, "instance", "mindmate.sqlite3")

    # Machine-learning files
    MODEL_PATH = os.path.join(BASE_DIR, "ml", "model", "mindmate_pipeline.joblib")
    METRICS_PATH = os.path.join(BASE_DIR, "ml", "model", "metrics.json")


    # Session cookie hardening. Set MINDMATE_HTTPS=1 when serving over HTTPS.
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.environ.get("MINDMATE_HTTPS") == "1"

    MAX_CONTENT_LENGTH = 64 * 1024  # small request bodies only
    MAX_CHAT_LENGTH = 1000
    MAX_NOTE_LENGTH = 500
    MAX_JOURNAL_LENGTH = 5000

    TESTING = False
