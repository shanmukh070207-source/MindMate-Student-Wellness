# MindMate — Project Guide

## What the project does

MindMate is a student-built web application for everyday study planning and basic wellness reflection. It brings a study planner, mood log, private journal, supportive response-based chat, breathing/grounding activities, resources, and a personal dashboard into one place.

It is a learning/demo project, not a medical product. It does not diagnose conditions, provide therapy, monitor people, or guarantee crisis detection. The chat's safety phrase check is limited and can miss messages or flag harmless ones. For immediate danger, contact local emergency services or a trusted person.

## Feature map

| Feature | Main route(s) | Implementation |
| --- | --- | --- |
| Landing page | `/` | `routes/main_routes.py`, `templates/index.html` |
| Register/login/logout | `/register`, `/login`, `/logout` | `routes/auth_routes.py`; Werkzeug password hashing |
| Dashboard | `/dashboard` | `routes/main_routes.py`, `charts.py`; personal summaries and charts |
| Supportive chat | `/chat`, `/chat/message` | `routes/chat_routes.py`, `ml/predict.py`, `ml/response_library.py` |
| Study planner | `/planner/` and task action routes | `routes/planner_routes.py`; add/edit/complete/delete/filter/sort |
| Mood tracker | `/mood/` | `routes/mood_routes.py`; predefined mood labels and optional note |
| Breathing and grounding | `/activities` | `routes/activity_routes.py`, `static/js/activities.js` |
| Private journal | `/journal` | `routes/activity_routes.py`; entries are scoped to the signed-in account |
| Wellness resources | `/resources`, `/safety` | `routes/resource_routes.py`, `routes/chat_routes.py` |

## Architecture

- **Frontend:** Jinja HTML templates, one shared base template, CSS, and vanilla JavaScript. No React or Node.js build step is needed. The existing visual design is kept as-is.
- **Backend:** Flask application factory in `app.py`; each feature has a Blueprint under `routes/`.
- **Database:** SQLite schema and connection helpers live in `database/`. User-owned records contain a `user_id` and queries filter by the logged-in user.
- **Classifier:** `ml/train_model.py` trains a TF-IDF + Logistic Regression pipeline from labelled CSV text. `ml/predict.py` loads the saved pipeline and applies a confidence threshold. Replies are selected from hand-written templates; the system is not a generative AI chatbot.
- **Charts:** `charts.py` uses Pandas and Matplotlib. Images are generated in memory and returned through a login-protected route.
- **Tests:** `tests/` contains pytest tests for routes, classifier behavior, planner/mood operations, and user-data separation.

## Data and privacy choices

- Chat messages are processed for the current request and are not written to the SQLite database by the chat feature.
- Mood notes and journal entries are personal data. They are stored in the local SQLite file under `instance/`, which is excluded from Git. The local file is not encrypted; do not use this demo for highly sensitive information or on a shared computer.
- The training script reads a labelled CSV dataset, not the application database. Never add private user chat, journal, or mood content to a training dataset.
- The included `data/demo_dataset.csv` is synthetic demonstration data, not real student research data. Its metrics must not be interpreted as real-world or clinical performance.
- The model file uses joblib/pickle-based serialization. Only load model files that you trained yourself or otherwise trust.

## Recommended development workflow

1. Create a feature branch for a larger change, or make a small focused change on `main`.
2. Change one feature at a time and keep the current frontend unless a UI change is specifically required.
3. Run the application and manually test the changed route in the browser.
4. Run automated tests with `python -m pytest -q` when dependencies are installed.
5. Commit the working change with a descriptive Git message.

## Current limitations / responsible improvements

- The classifier is a small text-pattern model trained on synthetic examples. It can misclassify context, slang, spelling variations, sarcasm, and other languages. It should be presented as a prototype only.
- Phrase-based safety detection is not dependable crisis screening. The app cannot call or alert anyone.
- There is no password reset, email verification, rate limiting, account recovery, encrypted database, or formal security review.
- For a public deployment, use a production WSGI server, HTTPS, a stable secret key from environment configuration, backups, dependency review, rate limiting, and a security/privacy review before allowing real users.
