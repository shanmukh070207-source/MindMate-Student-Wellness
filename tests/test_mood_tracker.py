import sqlite3


def rows(app):
    conn = sqlite3.connect(app.config["DATABASE"])
    conn.row_factory = sqlite3.Row
    return conn.execute("SELECT * FROM mood_entries ORDER BY id").fetchall()


def test_empty_state(auth_client):
    assert b"No mood entries yet" in auth_client.get("/mood/").data


def test_create_and_display_mood(app, auth_client):
    response = auth_client.post("/mood/add", data={"mood": "Stressed", "note": "Exam week"}, follow_redirects=True)
    assert b"Mood saved" in response.data
    page = auth_client.get("/mood/").data
    assert b"Stressed" in page and b"Exam week" in page
    assert len(rows(app)) == 1


def test_invalid_mood_rejected(app, auth_client):
    response = auth_client.post("/mood/add", data={"mood": "Ecstatic"}, follow_redirects=True)
    assert b"Please choose one of the mood options" in response.data
    assert rows(app) == []


def test_note_too_long_rejected(app, auth_client):
    auth_client.post("/mood/add", data={"mood": "Good", "note": "x" * 501})
    assert rows(app) == []


def test_delete_mood(app, auth_client):
    auth_client.post("/mood/add", data={"mood": "Good"})
    entry_id = rows(app)[0]["id"]
    auth_client.post(f"/mood/{entry_id}/delete")
    assert rows(app) == []


def test_notes_are_escaped(auth_client):
    auth_client.post("/mood/add", data={"mood": "Okay", "note": "<script>alert(1)</script>"})
    page = auth_client.get("/mood/").data
    assert b"<script>alert(1)</script>" not in page
