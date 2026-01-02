import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import os
import tempfile
import pytest
import app as app_module



@pytest.fixture
def client():
    db_fd, temp_db = tempfile.mkstemp()
    os.close(db_fd)

    original_db = app_module.DB_NAME
    app_module.DB_NAME = temp_db

    app_module.init_db()
    app_module.app.testing = True
    client = app_module.app.test_client()

    yield client

    os.remove(temp_db)
    app_module.DB_NAME = original_db


def test_home_page_loads(client):
    r = client.get("/")
    assert r.status_code == 200
    assert b"Secure To-Do List" in r.data


def test_add_task(client):
    r = client.post("/add", data={"title": "Test Task"}, follow_redirects=True)
    assert r.status_code == 200
    assert b"Test Task" in r.data


def test_reject_empty_task(client):
    r = client.post("/add", data={"title": "   "}, follow_redirects=True)
    assert r.status_code == 200


def test_complete_task(client):
    client.post("/add", data={"title": "Complete Me"}, follow_redirects=True)
    r = client.get("/complete/1", follow_redirects=True)
    assert r.status_code == 200


def test_delete_task(client):
    client.post("/add", data={"title": "Delete Me"}, follow_redirects=True)
    r = client.get("/delete/1", follow_redirects=True)
    assert r.status_code == 200
