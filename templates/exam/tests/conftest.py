import pytest
from fastapi.testclient import TestClient
from harness_app.config import Settings
from harness_app.main import create_app


@pytest.fixture
def settings(tmp_path):
    return Settings(
        _env_file=None, database_path=tmp_path / "test.sqlite3", workflow_enabled=True
    )


@pytest.fixture
def client(settings):
    with TestClient(create_app(settings), headers={"X-Requested-With": "Harness"}) as c:
        yield c
