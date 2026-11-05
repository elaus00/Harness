from pathlib import Path

from pydantic import BaseModel, Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Account(BaseModel):
    username: str = Field(min_length=1, max_length=80)
    role: str = Field(min_length=1, max_length=80)
    password: SecretStr = Field(min_length=12)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="HARNESS_",
        env_file=".env",
        extra="ignore",
        hide_input_in_errors=True,
    )
    database_path: Path = Path("data/harness.sqlite3")
    auth_enabled: bool = False
    accounts: list[Account] = []
    write_roles: list[str] = []
    cookie_secure: bool = False
    session_hours: int = Field(default=8, ge=1, le=168)
    allowed_origins: list[str] = [
        "http://127.0.0.1:8080",
        "http://localhost:8080",
    ]
    workflow_enabled: bool = False
    max_upload_bytes: int = Field(default=10 * 1024 * 1024, ge=1)

    @model_validator(mode="after")
    def validate_accounts(self):
        if not self.auth_enabled:
            return self
        if len(self.accounts) != 2 or len({a.role for a in self.accounts}) != 2:
            raise ValueError("HARNESS_ACCOUNTS: 서로 다른 역할의 두 계정이 필요합니다.")
        if len({a.username for a in self.accounts}) != 2:
            raise ValueError("HARNESS_ACCOUNTS: 계정 이름이 달라야 합니다.")
        roles = {a.role for a in self.accounts}
        if not self.write_roles or not set(self.write_roles) <= roles:
            raise ValueError("HARNESS_WRITE_ROLES: 쓰기를 허용할 역할을 지정하세요.")
        return self
