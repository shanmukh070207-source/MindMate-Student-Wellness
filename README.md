# MindMate — Student Mental Wellness Companion

*A little support for your everyday student life.*

MindMate is a student-built Flask web application that brings everyday study planning and basic wellness reflection together in one place. It includes a supportive response-based chat, study planner, mood tracker, dashboard charts, guided breathing, grounding activity, private journal, and wellness resources.

> **Important:** MindMate is an educational wellness prototype, not a medical, diagnostic, crisis-monitoring, or therapy service. It cannot reliably detect every crisis or replace professional support.

## Features

- **Supportive chat:** TF-IDF + Logistic Regression classifier with hand-written response templates, a confidence threshold, and a separate phrase-based safety check. It is not a generative AI assistant and chat messages are not saved.
- **Study planner:** create, edit, complete/reopen, delete, filter, and sort tasks.
- **Mood tracker:** record one of five moods with an optional note and view history.
- **Personal dashboard:** user-specific summaries and charts generated using Pandas and Matplotlib.
- **Stress-relief activities:** guided breathing and five-senses grounding.
- **Private journal:** create and delete journal entries tied to the signed-in account.
- **Accounts:** registration and login with password hashing; private pages and user-owned records are scoped to the current account.
- **Resources:** study habits, wellness guidance, and support information.
- **Responsive interface:** HTML templates, CSS, and vanilla JavaScript. No React or Node.js build is required.

## Technology

Python 3.10+, Flask, SQLite, scikit-learn, Pandas, Matplotlib, joblib, HTML, CSS, JavaScript, and pytest for tests.

## Folder structure

```text
MindMate/
├── app.py                       # Flask application factory and startup
├── config.py                    # App configuration and secret key
├── charts.py                    # Dashboard summaries and chart generation
├── requirements.txt             # Runtime packages
├── requirements-dev.txt         # Runtime packages plus pytest
├── run_mindmate_windows.bat     # Windows setup and launch helper
├── train_model_windows.bat      # Retrain the chat classifier on Windows
├── PROJECT_GUIDE.md             # Architecture, routes, privacy, limitations
├── database/                    # SQLite schema and helpers
├── routes/                      # Flask blueprints for each feature
├── ml/                           # Training, inference, response templates, safety check
│   └── model/                    # Trained demo model and evaluation metrics
├── data/                         # Synthetic demo dataset and instructions
├── templates/                    # Pages and shared layout
├── static/css/                   # Existing UI styles
├── static/js/                    # Frontend interactions
├── instance/                     # Local database (ignored by Git)
└── tests/                        # Automated tests
```

## Quick start — Windows

### Option A: simplest way

1. Extract the ZIP file.
2. Open the **inner `MindMate` folder** in VS Code. It must contain `app.py` and `requirements.txt` directly.
3. Double-click `run_mindmate_windows.bat`, or right-click it and choose **Open**.
4. The first run creates `.venv` and installs dependencies. This requires an internet connection.
5. When Flask starts, open <http://127.0.0.1:5000> in your browser.
6. Register a local account and log in.

If the batch file closes too quickly, open a terminal in the project folder and follow Option B.

### Option B: terminal commands

Open a terminal in the folder that contains `app.py` and run these commands one at a time:

```bat
python -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt
python app.py
```

Then visit <http://127.0.0.1:5000>.

If `python` is not recognized, install Python 3.10 or newer and enable **Add Python to PATH** during installation. On some Windows systems, use `py` instead of `python` for the first command.

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python app.py
```

## Retrain the chat classifier (optional)

A trained demonstration model is included, so you can normally start the app without training it again. To retrain from the included synthetic dataset:

```bash
python -m ml.train_model
```

To train from a different labelled CSV:

```bash
python -m ml.train_model --data data/my_dataset.csv
```

The CSV must contain `text` and `label` columns. See `data/README.md` for accepted labels, format, data-leakage notes, and licensing guidance. The training script writes the pipeline and evaluation metrics into `ml/model/`.

The included dataset is synthetic demonstration data. Metrics are only a rough exercise in evaluating a small demo dataset; they do not indicate how the classifier performs on real students or any clinical condition.

## Run tests

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

Tests use temporary databases and train a temporary model, so they do not modify the app's local database or use personal journal/mood entries as training data.

## Configuration

The app reads `MINDMATE_SECRET_KEY` from the environment. If not provided, a random key is generated each time the server starts, which means sessions are reset on restart. For stable local development, copy `.env.example` as a reference and set the environment variable in your terminal; the app does not automatically load `.env` files.

PowerShell example:

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
# Copy the printed value into the next command:
$env:MINDMATE_SECRET_KEY = "paste-your-generated-value-here"
python app.py
```

For HTTPS deployment only, set `MINDMATE_HTTPS=1` so session cookies are marked secure. Do not use the built-in Flask development server for production.

## Privacy and safety notes

- Mood notes and journal entries are stored locally in `instance/mindmate.sqlite3`. This database is not encrypted; keep the project on a trusted device and do not commit this file to GitHub.
- Chat messages are not saved by the chat route. Avoid entering identifying or highly sensitive information anyway.
- Passwords are stored as hashes, SQL queries use parameters, and personal records are filtered by account. These are good learning safeguards, but they do not constitute a formal security audit.
- The safety check uses simple phrase matching. It can miss risk or flag harmless messages, and MindMate does not contact anyone on a user's behalf. In immediate danger, contact local emergency services or a trusted person. Verify support contact details before any real-world deployment and adapt them to the location of your intended users.
- The serialized model file should only be loaded if it is trusted. Never replace it with an untrusted joblib file.

For a fuller walkthrough, route map, architecture, privacy decisions, and future improvements, see [`PROJECT_GUIDE.md`](PROJECT_GUIDE.md).
