import sqlite3
from contextlib import contextmanager
from urllib.parse import quote

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
 username TEXT PRIMARY KEY, role TEXT NOT NULL, password_hash TEXT NOT NULL,
 active INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE IF NOT EXISTS sessions (
 token_hash TEXT PRIMARY KEY, username TEXT NOT NULL REFERENCES users(username),
 expires_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS datasets (
 id TEXT PRIMARY KEY, files_json TEXT NOT NULL, profile_json TEXT NOT NULL,
 created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS jobs (
 id TEXT PRIMARY KEY, dataset_id TEXT NOT NULL REFERENCES datasets(id),
 status TEXT NOT NULL CHECK(status IN ('running','completed','failed')),
 config_json TEXT NOT NULL, plan_json TEXT, report_json TEXT, error_json TEXT,
 created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS runtime_state (
 id INTEGER PRIMARY KEY CHECK(id=1),
 active_dataset TEXT REFERENCES datasets(id), running_job TEXT
);
INSERT OR IGNORE INTO runtime_state(id) VALUES (1);
"""


@contextmanager
def connection(path, *, write=False):
    uri = "file:" + quote(str(path.resolve()), safe="/") + "?mode=rw"
    db = sqlite3.connect(uri, uri=True, timeout=10, isolation_level=None)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys=ON")
    try:
        if write:
            db.execute("BEGIN IMMEDIATE")
        yield db
        if write:
            db.commit()
    except BaseException:
        if write:
            db.rollback()
        raise
    finally:
        db.close()


def initialize(settings, passwords):
    path = settings.database_path
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as db:
        mode = db.execute("PRAGMA journal_mode=WAL").fetchone()[0]
        if mode.lower() != "wal":
            raise RuntimeError("SQLite WAL 모드를 사용할 수 없습니다.")
        db.executescript(SCHEMA)
    if not settings.auth_enabled:
        return
    with connection(path, write=True) as db:
        db.execute("UPDATE users SET active=0")
        for account in settings.accounts:
            old = db.execute(
                "SELECT * FROM users WHERE username=?", (account.username,)
            ).fetchone()
            raw = account.password.get_secret_value()
            same = old and passwords.verify(raw, old["password_hash"])
            hashed = old["password_hash"] if same else passwords.hash(raw)
            if old and (not same or old["role"] != account.role):
                db.execute("DELETE FROM sessions WHERE username=?", (account.username,))
            db.execute(
                "INSERT INTO users VALUES (?,?,?,1) ON CONFLICT(username) "
                "DO UPDATE SET role=excluded.role,password_hash=excluded.password_hash,"
                "active=1",
                (account.username, account.role, hashed),
            )
        db.execute(
            "DELETE FROM sessions WHERE username IN "
            "(SELECT username FROM users WHERE active=0)"
        )


def readiness(path):
    with connection(path) as db:
        db.execute(
            "SELECT s.id,d.id,j.id,u.username,t.token_hash "
            "FROM runtime_state s LEFT JOIN datasets d ON d.id=s.active_dataset "
            "LEFT JOIN jobs j ON j.id=s.running_job "
            "LEFT JOIN users u ON 0 LEFT JOIN sessions t ON 0"
        ).fetchall()
        if (
            db.execute("SELECT COUNT(*) FROM runtime_state WHERE id=1").fetchone()[0]
            != 1
        ):
            raise sqlite3.DatabaseError("runtime state missing")
