import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app


@pytest.fixture
def client(tmp_path):
    app = create_app(Settings(database_path=tmp_path / "test.sqlite3"))
    with TestClient(app, headers={"X-Requested-With": "Harness"}) as client:
        yield client
