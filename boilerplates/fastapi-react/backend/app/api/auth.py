import hashlib
import secrets
import sqlite3
import time

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pwdlib import PasswordHash
from pydantic import BaseModel, EmailStr, Field, field_validator

from app.core.database import get_db

router = APIRouter(prefix="/auth", tags=["auth"])
passwords = PasswordHash.recommended()
DUMMY_HASH = passwords.hash(secrets.token_urlsafe(32))
COOKIE = "harness_session"


def digest(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


class LoginInput(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value):
        return value.lower()


class RegisterInput(LoginInput):
    name: str = Field(min_length=1, max_length=60)
    password: str = Field(min_length=12, max_length=128)

    @field_validator("name")
    @classmethod
    def valid_name(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("이름을 입력하세요.")
        return value


class User(BaseModel):
    id: int
    email: str
    name: str


def require_user(request: Request, db=Depends(get_db, scope="function")) -> User:
    token = request.cookies.get(COOKIE, "")
    row = db.execute(
        "SELECT u.id,u.email,u.name FROM users u JOIN sessions s ON u.id=s.user_id "
        "WHERE s.token_hash=? AND s.expires_at>?",
        (digest(token), time.time()),
    ).fetchone()
    if not row:
        raise HTTPException(401, "다시 로그인해 주세요.")
    return User(**dict(row))


def throttle(request, db):
    # SQLite shares limits across workers; ignore untrusted forwarding headers.
    key = digest(request.client.host if request.client else "unknown")
    now = time.time()
    db.execute(
        "INSERT INTO auth_attempts VALUES (?,?,1) ON CONFLICT(key) DO UPDATE SET "
        "count=CASE WHEN started_at<? THEN 1 ELSE count+1 END, "
        "started_at=CASE WHEN started_at<? THEN ? ELSE started_at END",
        (key, now, now - 600, now - 600, now),
    )
    db.execute("DELETE FROM auth_attempts WHERE started_at<?", (now - 3600,))
    count = db.execute(
        "SELECT count FROM auth_attempts WHERE key=?", (key,)
    ).fetchone()[0]
    db.commit()
    if count > 30:
        raise HTTPException(
            429,
            "요청이 너무 많습니다. 잠시 후 다시 시도하세요.",
            headers={"Retry-After": "600"},
        )


def start_session(user, request, response, db):
    token = secrets.token_urlsafe(32)
    ttl = request.app.state.settings.session_hours * 3600
    old = request.cookies.get(COOKIE)
    if old:
        db.execute("DELETE FROM sessions WHERE token_hash=?", (digest(old),))
    db.execute("DELETE FROM sessions WHERE expires_at<=?", (time.time(),))
    db.execute(
        "INSERT INTO sessions VALUES (?,?,?)",
        (digest(token), user.id, time.time() + ttl),
    )
    response.set_cookie(
        COOKIE,
        token,
        max_age=ttl,
        httponly=True,
        samesite="lax",
        secure=request.app.state.settings.cookie_secure,
        path="/api/v1",
    )
    response.headers["Cache-Control"] = "no-store"
    return user


@router.post("/register", response_model=User, status_code=201)
def register(
    data: RegisterInput,
    request: Request,
    response: Response,
    db=Depends(get_db, scope="function"),
):
    throttle(request, db)
    hashed = passwords.hash(data.password)
    try:
        cursor = db.execute(
            "INSERT INTO users(email,name,password_hash) VALUES (?,?,?)",
            (str(data.email), data.name, hashed),
        )
    except sqlite3.IntegrityError:
        raise HTTPException(
            409, "이 이메일로 가입할 수 없습니다. 로그인 정보를 확인하세요."
        ) from None
    user = User(id=cursor.lastrowid, email=str(data.email), name=data.name)
    return start_session(user, request, response, db)


@router.post("/login", response_model=User)
def login(
    data: LoginInput,
    request: Request,
    response: Response,
    db=Depends(get_db, scope="function"),
):
    throttle(request, db)
    row = db.execute("SELECT * FROM users WHERE email=?", (str(data.email),)).fetchone()
    valid = passwords.verify(data.password, row["password_hash"] if row else DUMMY_HASH)
    if not row or not valid:
        raise HTTPException(401, "이메일 또는 비밀번호를 확인하세요.")
    return start_session(
        User(id=row["id"], email=row["email"], name=row["name"]), request, response, db
    )


@router.get("/me", response_model=User)
def me(user=Depends(require_user)):
    return user


@router.post("/logout", status_code=204)
def logout(request: Request, response: Response, db=Depends(get_db, scope="function")):
    db.execute(
        "DELETE FROM sessions WHERE token_hash=?",
        (digest(request.cookies.get(COOKIE, "")),),
    )
    response.delete_cookie(
        COOKIE,
        path="/api/v1",
        httponly=True,
        secure=request.app.state.settings.cookie_secure,
        samesite="lax",
    )
