import sqlite3
from datetime import date, timedelta

from routes.planner_routes import validate_task_form


def iso(days):
    return (date.today() + timedelta(days=days)).isoformat()


def rows(app):
    conn = sqlite3.connect(app.config["DATABASE"])
    conn.row_factory = sqlite3.Row
    return conn.execute("SELECT * FROM study_tasks ORDER BY id").fetchall()


def add(client, title="Read chapter 3", due=None, subject="Physics", description="pages 10-20"):
    return client.post("/planner/add", data={"title": title, "due_date": iso(3) if due is None else due,
                                             "subject": subject, "description": description},
                       follow_redirects=True)


def test_create_task(app, auth_client):
    response = add(auth_client)
    assert b"Task added" in response.data
    assert len(rows(app)) == 1 and rows(app)[0]["title"] == "Read chapter 3"


def test_invalid_input_rejected(app, auth_client):
    assert b"Please enter a task title" in add(auth_client, title="  ").data
    assert b"not a valid date" in add(auth_client, due="2026-13-45").data
    assert b"Please choose a due date" in add(auth_client, due="").data
    assert rows(app) == []


def test_missing_due_date_rejected(app, auth_client):
    response = auth_client.post("/planner/add", data={"title": "x"}, follow_redirects=True)
    assert b"Please choose a due date" in response.data and rows(app) == []


def test_edit_task(app, auth_client):
    add(auth_client)
    task_id = rows(app)[0]["id"]
    response = auth_client.post(f"/planner/{task_id}/edit",
                                data={"title": "New title", "due_date": iso(5), "subject": "Maths", "description": ""},
                                follow_redirects=True)
    assert b"Task updated" in response.data
    assert rows(app)[0]["title"] == "New title" and rows(app)[0]["subject"] == "Maths"


def test_edit_with_invalid_data_keeps_old_values(app, auth_client):
    add(auth_client)
    task_id = rows(app)[0]["id"]
    response = auth_client.post(f"/planner/{task_id}/edit", data={"title": "", "due_date": "bad"})
    assert response.status_code == 400
    assert rows(app)[0]["title"] == "Read chapter 3"


def test_complete_and_reopen_task(app, auth_client):
    add(auth_client)
    task_id = rows(app)[0]["id"]
    auth_client.post(f"/planner/{task_id}/toggle")
    assert rows(app)[0]["status"] == "completed"
    assert b"Read chapter 3" in auth_client.get("/planner/?view=completed").data
    auth_client.post(f"/planner/{task_id}/toggle")
    assert rows(app)[0]["status"] == "pending"


def test_delete_task(app, auth_client):
    add(auth_client)
    task_id = rows(app)[0]["id"]
    auth_client.post(f"/planner/{task_id}/delete")
    assert rows(app) == []


def test_overdue_and_upcoming_views(app, auth_client):
    add(auth_client, title="Late task", due=iso(-2))
    add(auth_client, title="Future task", due=iso(4))
    overdue = auth_client.get("/planner/?view=overdue").data
    upcoming = auth_client.get("/planner/?view=upcoming").data
    assert b"Late task" in overdue and b"Future task" not in overdue
    assert b"Future task" in upcoming and b"Late task" not in upcoming


def test_completed_task_is_not_overdue(app, auth_client):
    add(auth_client, title="Old but done", due=iso(-5))
    auth_client.post(f"/planner/{rows(app)[0]['id']}/toggle")
    assert b"Old but done" not in auth_client.get("/planner/?view=overdue").data


def test_sort_by_due_date(app, auth_client):
    add(auth_client, title="Later task", due=iso(10))
    add(auth_client, title="Sooner task", due=iso(1))
    asc = auth_client.get("/planner/?order=asc").data.decode()
    desc = auth_client.get("/planner/?order=desc").data.decode()
    assert asc.index("Sooner task") < asc.index("Later task")
    assert desc.index("Later task") < desc.index("Sooner task")


def test_validate_task_form_pure():
    values, errors = validate_task_form({"title": "T", "due_date": "2026-02-30"})
    assert errors and values["due_date"] is None
    values, errors = validate_task_form({"title": "T", "due_date": "2026-02-20"})
    assert not errors and values["due_date"] == "2026-02-20"
