import hashlib
import secrets
import time

from fastapi import Depends, Request, Response
from pydantic import BaseModel, Field

from .database import connection
from .errors import Fault

COOKIE = "harness_session"


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


class Login(BaseModel):
    username: str = Field(min_length=1, max_length=80)
    password: str = Field(min_length=1, max_length=128)


def current_user(request: Request):
    config = request.app.state.settings
    if not config.auth_enabled:
        return {"username": None, "role": None, "auth_enabled": False}
    with connection(config.database_path) as db:
        user = db.execute(
            "SELECT u.username,u.role FROM sessions s JOIN users u USING(username) "
            "WHERE s.token_hash=? AND s.expires_at>? AND u.active=1",
            (digest(request.cookies.get(COOKIE, "")), time.time()),
        ).fetchone()
    if not user:
        raise Fault(401, "authentication_required", "로그인이 필요합니다.")
    return {**dict(user), "auth_enabled": True}


def write_user(request: Request, user=Depends(current_user)):
    if (
        request.app.state.settings.auth_enabled
        and user["role"] not in request.app.state.settings.write_roles
    ):
        raise Fault(403, "permission_denied", "이 작업을 수행할 권한이 없습니다.")
    return user


def login(data: Login, request: Request, response: Response):
    config = request.app.state.settings
    if not config.auth_enabled:
        raise Fault(409, "auth_disabled", "인증 기능이 꺼져 있습니다.")
    with connection(config.database_path, write=True) as db:
        user = db.execute(
            "SELECT * FROM users WHERE username=? AND active=1", (data.username,)
        ).fetchone()
        passwords = request.app.state.passwords
        valid = passwords.verify(
            data.password,
            user["password_hash"] if user else request.app.state.dummy_hash,
        )
        if not valid or not user:
            raise Fault(401, "invalid_credentials", "계정과 비밀번호를 확인하세요.")
        db.execute(
            "DELETE FROM sessions WHERE expires_at<=? OR token_hash=?",
            (time.time(), digest(request.cookies.get(COOKIE, ""))),
        )
        token = secrets.token_urlsafe(32)
        ttl = config.session_hours * 3600
        db.execute(
            "INSERT INTO sessions VALUES (?,?,?)",
            (digest(token), user["username"], time.time() + ttl),
        )
    response.set_cookie(
        COOKIE,
        token,
        max_age=ttl,
        httponly=True,
        samesite="lax",
        secure=config.cookie_secure,
        path="/api",
    )
    return {"username": user["username"], "role": user["role"]}


def logout(request: Request, response: Response):
    with connection(request.app.state.settings.database_path, write=True) as db:
        db.execute(
            "DELETE FROM sessions WHERE token_hash=?",
            (digest(request.cookies.get(COOKIE, "")),),
        )
    response.delete_cookie(
        COOKIE,
        path="/api",
        secure=request.app.state.settings.cookie_secure,
        httponly=True,
        samesite="lax",
    )
    return {"logged_out": True}
