import sqlite3
from datetime import date, timedelta


def test_summary_matches_database(app, auth_client):
    due = (date.today() + timedelta(days=2)).isoformat()
    for title in ("A", "B", "C"):
        auth_client.post("/planner/add", data={"title": title, "due_date": due})
    conn = sqlite3.connect(app.config["DATABASE"])
    first = conn.execute("SELECT id FROM study_tasks ORDER BY id").fetchone()[0]
    auth_client.post(f"/planner/{first}/toggle")
    auth_client.post("/mood/add", data={"mood": "Good"})
    auth_client.post("/mood/add", data={"mood": "Low"})

    import charts
    from database.db import get_db
    with app.app_context():
        counts = charts.summary_counts(get_db(), 1)
    assert counts["pending"] == 2 and counts["completed"] == 1 and counts["mood_count"] == 2

    page = auth_client.get("/dashboard").data.decode()
    assert "mood_trend.png" in page and "tasks.png" in page


def test_charts_are_png_and_use_real_data(auth_client):
    auth_client.post("/mood/add", data={"mood": "Good"})
    response = auth_client.get("/charts/mood_trend.png")
    assert response.status_code == 200 and response.data.startswith(b"\x89PNG")


def test_charts_404_without_data(auth_client):
    assert auth_client.get("/charts/mood_trend.png").status_code == 404
    assert auth_client.get("/charts/tasks.png").status_code == 404
    assert auth_client.get("/charts/unknown.png").status_code == 404


def test_empty_dashboard_has_no_chart_images(auth_client):
    page = auth_client.get("/dashboard").data
    assert b"/charts/" not in page


def test_charts_require_login(client):
    assert client.get("/charts/mood_trend.png").status_code == 302


def test_chart_functions_handle_empty_data(app):
    import charts
    from database.db import get_db
    with app.app_context():
        # a user id that has no data at all
        for func in (charts.mood_trend_chart, charts.mood_distribution_chart, charts.task_status_chart):
            assert func(get_db(), 999) is None


def test_other_users_cannot_see_or_change_records(app, make_client):
    alice, bob = make_client("alice_a"), make_client("bob_b")
    due = (date.today() + timedelta(days=2)).isoformat()
    alice.post("/planner/add", data={"title": "Alice secret task", "due_date": due})
    alice.post("/mood/add", data={"mood": "Low", "note": "alice private note"})
    alice.post("/journal/add", data={"entry_text": "alice private journal"})

    conn = sqlite3.connect(app.config["DATABASE"])
    task_id = conn.execute("SELECT id FROM study_tasks").fetchone()[0]
    mood_id = conn.execute("SELECT id FROM mood_entries").fetchone()[0]
    journal_id = conn.execute("SELECT id FROM journal_entries").fetchone()[0]

    for path in ["/planner/", "/mood/", "/journal", "/dashboard"]:
        page = bob.get(path).data
        assert b"Alice secret task" not in page and b"alice private" not in page

    # Changing the id in the URL gives 404 and changes nothing
    assert bob.get(f"/planner/{task_id}/edit").status_code == 404
    assert bob.post(f"/planner/{task_id}/toggle").status_code == 404
    assert bob.post(f"/planner/{task_id}/delete").status_code == 404
    assert bob.post(f"/mood/{mood_id}/delete").status_code == 404
    assert bob.post(f"/journal/{journal_id}/delete").status_code == 404
    assert conn.execute("SELECT COUNT(*) FROM study_tasks").fetchone()[0] == 1
    assert conn.execute("SELECT COUNT(*) FROM mood_entries").fetchone()[0] == 1
    assert conn.execute("SELECT COUNT(*) FROM journal_entries").fetchone()[0] == 1


def test_journal_save_and_delete(app, auth_client):
    auth_client.post("/journal/add", data={"entry_text": "today was long"})
    assert b"today was long" in auth_client.get("/journal").data
    conn = sqlite3.connect(app.config["DATABASE"])
    entry_id = conn.execute("SELECT id FROM journal_entries").fetchone()[0]
    auth_client.post(f"/journal/{entry_id}/delete")
    assert conn.execute("SELECT COUNT(*) FROM journal_entries").fetchone()[0] == 0
    assert b"Your journal is empty" in auth_client.get("/journal").data


def test_empty_journal_entry_rejected(app, auth_client):
    auth_client.post("/journal/add", data={"entry_text": "   "})
    conn = sqlite3.connect(app.config["DATABASE"])
    assert conn.execute("SELECT COUNT(*) FROM journal_entries").fetchone()[0] == 0


def test_chat_messages_are_not_stored(app, auth_client):
    auth_client.post("/chat/message", json={"message": "I am worried about my exams so much"})
    conn = sqlite3.connect(app.config["DATABASE"])
    tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")]
    assert not any("chat" in t for t in tables)
    for table in tables:
        dump = str(conn.execute(f"SELECT * FROM {table}").fetchall())
        assert "worried about my exams" not in dump


def test_training_code_never_reads_the_database():
    """Journal entries and chat text must not become training data."""
    import inspect
    from ml import train_model
    source = inspect.getsource(train_model)
    assert "sqlite" not in source.lower() and "journal" not in source.lower()
