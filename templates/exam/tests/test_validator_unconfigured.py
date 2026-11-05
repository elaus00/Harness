from fastapi.testclient import TestClient
from harness_app.main import create_app

from contracts import ValidationReport


def test_implemented_generator_cannot_bypass_unconfigured_validator(settings):
    with TestClient(
        create_app(settings, generator=lambda dataset, config: {}),
        headers={"X-Requested-With": "Harness"},
    ) as c:
        c.post("/api/datasets/apply", json={"files": {"x.csv": "x\n1\n"}})
        response = c.post("/api/jobs", json={})
        assert response.status_code == 501
        assert c.get("/api/jobs").json()["jobs"][0]["plan"] is None


def test_not_implemented_report_is_not_a_pass(settings):
    app = create_app(
        settings,
        generator=lambda dataset, config: {},
        validator=lambda dataset, plan: ValidationReport("not_implemented"),
    )
    with TestClient(app, headers={"X-Requested-With": "Harness"}) as c:
        c.post("/api/datasets/apply", json={"files": {"x.csv": "x\n1\n"}})
        assert c.post("/api/jobs", json={}).status_code == 501
