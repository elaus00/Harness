import time

from app.api.auth import COOKIE, digest
from app.core.database import connection

BASE = "/api/v1"
ACCOUNT = {
    "email": "person@example.com",
    "password": "test-password-123",
    "name": "테스터",
}


def register(client, email="person@example.com"):
    return client.post(BASE + "/auth/register", json={**ACCOUNT, "email": email})


def test_registration_session_and_revoke(client):
    response = register(client)
    assert response.status_code == 201
    assert "password" not in str(response.json())
    cookie = response.headers["set-cookie"]
    assert "HttpOnly" in cookie and "SameSite=lax" in cookie
    token = client.cookies.get(COOKIE)
    assert client.get(BASE + "/auth/me").json()["name"] == "테스터"
    with connection(client.app.state.settings.database_path) as db:
        hashed = db.execute("SELECT password_hash FROM users").fetchone()[0]
        assert hashed.startswith("$argon2") and hashed != ACCOUNT["password"]
        assert db.execute("SELECT token_hash FROM sessions").fetchone()[0] == digest(
            token
        )
    assert client.post(BASE + "/auth/logout").status_code == 204
    assert client.get(BASE + "/auth/me").status_code == 401
    client.cookies.set(COOKIE, token)
    assert client.get(BASE + "/workspace").status_code == 401


def test_login_failure_rotation_and_expiry(client):
    register(client)
    old = client.cookies.get(COOKIE)
    bad = client.post(BASE + "/auth/login", json={**ACCOUNT, "password": "incorrect"})
    assert bad.status_code == 401
    assert client.post(BASE + "/auth/login", json=ACCOUNT).status_code == 200
    new = client.cookies.get(COOKIE)
    assert new != old
    with connection(client.app.state.settings.database_path) as db:
        assert not db.execute(
            "SELECT 1 FROM sessions WHERE token_hash=?", (digest(old),)
        ).fetchone()
        db.execute("UPDATE sessions SET expires_at=?", (time.time() - 1,))
    assert client.get(BASE + "/workspace").status_code == 401


def test_validation_and_duplicate(client):
    assert (
        client.post(
            BASE + "/auth/register", json={**ACCOUNT, "password": "short"}
        ).status_code
        == 422
    )
    assert register(client).status_code == 201
    assert register(client, "PERSON@example.com").status_code == 409


def test_cross_origin_and_missing_csrf_header(client):
    assert (
        client.post(
            BASE + "/auth/register",
            json=ACCOUNT,
            headers={"Origin": "https://evil.example"},
        ).status_code
        == 403
    )
    assert (
        client.post(
            BASE + "/auth/register", json=ACCOUNT, headers={"X-Requested-With": ""}
        ).status_code
        == 403
    )
    assert client.get(BASE + "/workspace").status_code == 401


def test_rate_limit(client):
    with connection(client.app.state.settings.database_path) as db:
        db.execute(
            "INSERT INTO auth_attempts VALUES (?,?,?)",
            (digest("testclient"), time.time(), 30),
        )
    assert register(client).status_code == 429


def test_task_ownership_and_persistence(client):
    register(client)
    task = client.post(BASE + "/tasks", json={"title": "개인 업무"}).json()
    assert (
        client.patch(BASE + f"/tasks/{task['id']}", json={"status": "done"}).status_code
        == 200
    )
    assert client.get(BASE + "/workspace").json()["tasks"][0]["status"] == "done"
    client.post(BASE + "/auth/logout")
    register(client, "other@example.com")
    assert client.get(BASE + "/workspace").json()["tasks"] == []
    assert (
        client.patch(BASE + f"/tasks/{task['id']}", json={"status": "todo"}).status_code
        == 404
    )
    client.post(BASE + "/auth/logout")
    client.post(BASE + "/auth/login", json=ACCOUNT)
    assert len(client.get(BASE + "/workspace").json()["tasks"]) == 1


def test_sample_is_opt_in_and_not_duplicated(client):
    register(client)
    assert client.get(BASE + "/workspace").json()["tasks"] == []
    assert client.post(BASE + "/tasks/sample").status_code == 201
    assert client.post(BASE + "/tasks/sample").status_code == 409
    assert len(client.get(BASE + "/workspace").json()["tasks"]) == 7


def test_secure_cookie_configuration(client):
    client.app.state.settings.cookie_secure = True
    assert "Secure" in register(client).headers["set-cookie"]
