from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="HARNESS_", env_file=".env", extra="ignore"
    )
    database_path: Path = Path("data/harness.sqlite3")
    cookie_secure: bool = False
    session_hours: int = 8
    allowed_origins: list[str] = ["http://127.0.0.1:5173", "http://localhost:5173"]
