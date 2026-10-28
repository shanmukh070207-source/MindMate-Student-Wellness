"""Create the SQLite database tables.

Usage (from the MindMate folder):
    python -m database.init_db
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import Config  # noqa: E402
from database.db import init_db  # noqa: E402


def main():
    try:
        init_db(Config.DATABASE)
    except Exception as exc:  # report clearly, no stack trace for the user
        print(f"Could not initialize the database: {exc}")
        sys.exit(1)
    print(f"Database ready at {Config.DATABASE}")


if __name__ == "__main__":
    main()
