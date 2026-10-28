from conftest import register_and_login
from app import create_app


def test_home_page_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"A little support for your everyday student life." in response.data


def test_dashboard_requires_login(client):
    response = client.get("/dashboard")
    assert response.status_code == 302 and "/login" in response.headers["Location"]


def test_dashboard_loads_with_empty_data(auth_client):
    response = auth_client.get("/dashboard")
    assert response.status_code == 200
    assert b"No pending tasks" in response.data
    assert b"No moods recorded yet" in response.data


def test_unknown_route_shows_404_page(client):
    response = client.get("/this-page-does-not-exist")
    assert response.status_code == 404
    assert b"Page not found" in response.data


def test_register_validation_and_duplicate(client):
    bad = client.post("/register", data={"username": "a", "password": "short", "confirm": "short"})
    assert b"Username must be" in bad.data
    client.post("/register", data={"username": "bob_1", "password": "password123", "confirm": "password123"})
    dup = client.post("/register", data={"username": "bob_1", "password": "password123", "confirm": "password123"})
    assert b"already taken" in dup.data


def test_wrong_password_rejected(client):
    client.post("/register", data={"username": "carol", "password": "password123", "confirm": "password123"})
    response = client.post("/login", data={"username": "carol", "password": "wrongpass"})
    assert b"Incorrect username or password" in response.data


def test_password_is_hashed(app, client):
    register_and_login(client, "dave")
    import sqlite3
    row = sqlite3.connect(app.config["DATABASE"]).execute("SELECT password_hash FROM users").fetchone()
    assert "password123" not in row[0] and len(row[0]) > 30


def test_all_main_pages_load_when_logged_in(auth_client):
    for path in ["/chat", "/planner/", "/mood/", "/activities", "/journal", "/resources", "/safety"]:
        assert auth_client.get(path).status_code == 200, path


def test_csrf_enforced_when_enabled(tmp_path, trained_paths):
    app = create_app({"TESTING": True, "DATABASE": str(tmp_path / "c.sqlite3"),
                      "MODEL_PATH": trained_paths[0], "SECRET_KEY": "k"})
    c = app.test_client()
    response = c.post("/register", data={"username": "eve_1", "password": "password123", "confirm": "password123"})
    assert response.status_code == 400


def test_open_redirect_blocked(client):
    client.post("/register", data={"username": "frank", "password": "password123", "confirm": "password123"})
    response = client.post("/login?next=//evil.example", data={"username": "frank", "password": "password123"})
    assert "evil.example" not in response.headers["Location"]
