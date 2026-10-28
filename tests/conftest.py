import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app  # noqa: E402
from ml import train_model  # noqa: E402


@pytest.fixture(scope="session")
def trained_paths(tmp_path_factory):
    """Train a fresh model into a temp folder so tests don't depend on the repo's model file."""
    folder = tmp_path_factory.mktemp("model")
    model_path = str(folder / "pipeline.joblib")
    metrics_path = str(folder / "metrics.json")
    train_model.train(train_model.DEFAULT_DATA, model_path, metrics_path)
    return model_path, metrics_path


@pytest.fixture()
def app(tmp_path, trained_paths):
    application = create_app({
        "TESTING": True,
        "TESTING_SKIP_CSRF": True,
        "DATABASE": str(tmp_path / "test.sqlite3"),
        "MODEL_PATH": trained_paths[0],
        "SECRET_KEY": "test-key",
    })
    yield application


@pytest.fixture()
def client(app):
    return app.test_client()


def register_and_login(client, username="alice", password="password123"):
    client.post("/register", data={"username": username, "password": password, "confirm": password})
    return client.post("/login", data={"username": username, "password": password}, follow_redirects=True)


@pytest.fixture()
def auth_client(client):
    register_and_login(client)
    return client


@pytest.fixture()
def make_client(app):
    """Create extra logged-in clients (for cross-user privacy tests)."""
    def _make(username):
        c = app.test_client()
        register_and_login(c, username)
        return c
    return _make
