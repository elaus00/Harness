import time

from fastapi.testclient import TestClient
from harness_app.auth import COOKIE
from harness_app.config import Settings
from harness_app.database import connection
from harness_app.main import create_app

# Test-only fixtures, never initial application credentials.
PASSWORD = "test-only-password-123"
ACCOUNTS = [
    {"username": "writer", "role": "edit", "password": PASSWORD},
    {"username": "reader", "role": "view", "password": PASSWORD},
]
HEADERS = {"X-Requested-With": "Harness"}


def test_roles_are_enforced_on_server_and_session_revoked(tmp_path):
    settings = Settings(
        _env_file=None,
        database_path=tmp_path / "auth.sqlite3",
        auth_enabled=True,
        accounts=ACCOUNTS,
        write_roles=["edit"],
        workflow_enabled=True,
    )
    with TestClient(create_app(settings), headers=HEADERS) as c:
        assert c.get("/api/datasets").status_code == 401
        response = c.post(
            "/api/auth/login", json={"username": "reader", "password": PASSWORD}
        )
        assert response.status_code == 200
        assert "HttpOnly" in response.headers["set-cookie"]
        assert "SameSite=lax" in response.headers["set-cookie"]
        assert c.get("/api/datasets").status_code == 200
        assert (
            c.post(
                "/api/datasets/apply",
                json={"files": {"x.csv": "a\n1\n"}},
                headers={"X-Role": "edit"},
            ).status_code
            == 403
        )
        assert c.post("/api/jobs", json={}).status_code == 403
        old = c.cookies.get(COOKIE)
        assert c.post("/api/auth/logout").status_code == 200
        c.cookies.set(COOKIE, old)
        assert c.get("/api/datasets").status_code == 401
        c.cookies.clear()
        c.post("/api/auth/login", json={"username": "writer", "password": PASSWORD})
        assert (
            c.post(
                "/api/datasets/apply", json={"files": {"x.csv": "a\n1\n"}}
            ).status_code
            == 200
        )
        with connection(settings.database_path, write=True) as db:
            assert (
                db.execute("SELECT password_hash FROM users").fetchone()[0] != PASSWORD
            )
            db.execute("UPDATE sessions SET expires_at=?", (time.time() - 1,))
        assert c.get("/api/auth/me").status_code == 401


def test_seed_reconciles_password_and_preserves_data(tmp_path):
    settings = Settings(
        _env_file=None,
        database_path=tmp_path / "restart.sqlite3",
        auth_enabled=True,
        accounts=ACCOUNTS,
        write_roles=["edit"],
        cookie_secure=True,
        workflow_enabled=True,
    )
    with TestClient(
        create_app(settings), headers=HEADERS, base_url="https://localhost"
    ) as c:
        login = c.post(
            "/api/auth/login", json={"username": "writer", "password": PASSWORD}
        )
        assert "Secure" in login.headers["set-cookie"]
        cookie = c.cookies.get(COOKIE)
        version = c.post(
            "/api/datasets/apply", json={"files": {"x.csv": "a\n1\n"}}
        ).json()["version"]
    settings.accounts[0].password = type(settings.accounts[0].password)(
        "another-test-password"
    )
    with TestClient(
        create_app(settings), headers=HEADERS, base_url="https://localhost"
    ) as c:
        c.cookies.set(COOKIE, cookie)
        assert c.get("/api/auth/me").status_code == 401
        # Remove the manually injected replay cookie before testing browser login.
        c.cookies.clear()
        assert (
            c.post(
                "/api/auth/login", json={"username": "writer", "password": PASSWORD}
            ).status_code
            == 401
        )
        assert (
            c.post(
                "/api/auth/login",
                json={"username": "writer", "password": "another-test-password"},
            ).status_code
            == 200
        )
        assert c.get("/api/datasets").json()["active_version"] == version
