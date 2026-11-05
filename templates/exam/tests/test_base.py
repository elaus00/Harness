import sqlite3

import pytest
from fastapi.testclient import TestClient
from harness_app.config import Settings
from harness_app.database import connection
from harness_app.main import create_app
from pydantic import ValidationError


def test_ui_api_database_and_wal(client, settings):
    assert client.get("/").status_code == 200
    assert "/assets/app.js" in client.get("/").text
    assert client.get("/assets/app.js").status_code == 200
    assert client.get("/api/health").json() == {"status": "ok", "database": "ready"}
    with connection(settings.database_path) as db:
        assert db.execute("PRAGMA journal_mode").fetchone()[0] == "wal"


def test_readiness_is_not_process_liveness(client, settings):
    with connection(settings.database_path, write=True) as db:
        db.execute("DROP TABLE jobs")
    response = client.get("/api/health")
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "database_unavailable"


def test_missing_database_does_not_get_recreated(client, settings):
    settings.database_path.unlink()
    assert client.get("/api/health").status_code == 503
    assert not settings.database_path.exists()


def test_config_and_shared_error_contract(client):
    assert client.get("/api/config").json()["auth_enabled"] is False
    assert client.post("/api/jobs", json=[]).status_code == 422
    issue = client.get("/not-found").json()["error"]["issues"][0]
    assert {"file", "row", "column", "reason"} <= issue.keys()
    response = client.post(
        "/api/jobs", json={}, headers={"Origin": "https://other.test"}
    )
    assert response.status_code == 403


def test_workflow_can_be_excluded(tmp_path):
    config = Settings(_env_file=None, database_path=tmp_path / "base.sqlite3")
    with TestClient(create_app(config)) as c:
        assert c.get("/api/config").json()["workflow_enabled"] is False
        assert c.get("/api/datasets").status_code == 404


def test_required_auth_settings_fail_without_secrets():
    with pytest.raises(ValidationError, match="HARNESS_ACCOUNTS"):
        Settings(_env_file=None, auth_enabled=True)
    secret = "test-only-password"
    with pytest.raises(ValidationError) as error:
        Settings(
            _env_file=None,
            auth_enabled=True,
            accounts=[
                {"username": "a", "role": "one", "password": secret},
                {"username": "b", "role": "two", "password": secret},
            ],
        )
    assert "HARNESS_WRITE_ROLES" in str(error.value)
    assert secret not in str(error.value)


def test_invalid_db_location_fails_startup(tmp_path):
    parent = tmp_path / "not-a-directory"
    parent.write_text("keep")
    config = Settings(_env_file=None, database_path=parent / "data.sqlite3")
    with pytest.raises((OSError, sqlite3.Error)):
        with TestClient(create_app(config)):
            pass
