import json
import threading
from concurrent.futures import ThreadPoolExecutor

import pytest
from fastapi.testclient import TestClient
from harness_app import jobs
from harness_app.database import connection
from harness_app.main import create_app
from harness_app.recover import recover

from contracts import Issue, ValidationReport

HEADERS = {"X-Requested-With": "Harness"}
FILES = {"input.csv": "id,value\n001,2\n002,\n"}


def good_plan(dataset, config):
    # Test stub only; no application algorithm is supplied.
    return {"test_result": config.get("test_value", 1)}


def passed(dataset, plan):
    return ValidationReport("passed")


def apply(c, files=FILES):
    response = c.post("/api/datasets/apply", json={"files": files})
    assert response.status_code == 200, response.text
    return response.json()["version"]


def test_profile_preserves_strings_and_missing_values(client):
    response = client.post("/api/datasets/validate", json={"files": FILES})
    assert response.status_code == 200
    data = response.json()
    assert data["domain_checked"] is False
    profile = data["files"]["input.csv"]
    assert profile["rows"] == 2
    assert profile["dtypes"]["id"] == "String"
    assert profile["nulls"]["value"] == 1
    assert client.get("/api/datasets").json()["active_version"] is None


def test_bad_csv_does_not_replace_active_dataset(client):
    old = apply(client)
    for files in [
        {"bad.csv": "a,b\n1,2,3\n"},
        {"bad.csv": "a,a\n1,2\n"},
        {"../escape.csv": "a\n1\n"},
        {"empty.csv": ""},
    ]:
        response = client.post("/api/datasets/apply", json={"files": files})
        assert response.status_code == 422
        issue = response.json()["error"]["issues"][0]
        assert {"file", "row", "column", "reason"} <= issue.keys()
        assert client.get("/api/datasets").json()["active_version"] == old


def test_apply_rolls_back_both_insert_and_activation(client, settings):
    old = apply(client)
    with connection(settings.database_path, write=True) as db:
        db.execute(
            "CREATE TRIGGER reject_activation BEFORE UPDATE ON runtime_state "
            "BEGIN SELECT RAISE(ABORT, 'test transaction rollback'); END"
        )
    response = client.post("/api/datasets/apply", json={"files": {"new.csv": "x\n2\n"}})
    assert response.status_code == 503
    with connection(settings.database_path) as db:
        assert db.execute("SELECT COUNT(*) FROM datasets").fetchone()[0] == 1
        assert (
            db.execute("SELECT active_dataset FROM runtime_state").fetchone()[0] == old
        )


def test_unimplemented_engine_fails_explicitly_and_releases_lock(client, settings):
    apply(client)
    response = client.post("/api/jobs", json={})
    assert response.status_code == 501
    assert response.json()["error"]["code"] == "not_implemented"
    data = client.get("/api/jobs").json()["jobs"][0]
    assert data["status"] == "failed" and data["plan"] is None
    assert client.get(f"/api/jobs/{data['id']}/export").status_code == 409
    with connection(settings.database_path) as db:
        assert db.execute("SELECT running_job FROM runtime_state").fetchone()[0] is None


def test_versions_staleness_and_export(settings, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    app = create_app(settings, generator=good_plan, validator=passed)
    with TestClient(app, headers=HEADERS) as c:
        version = apply(c)
        response = c.post("/api/jobs", json={"test_value": 7})
        assert response.status_code == 200
        job = response.json()
        assert job["dataset_version"] == version
        assert job["plan"] == {"test_result": 7}
        url = f"/api/jobs/{job['id']}/export"
        assert c.get(url).json()["report"]["status"] == "passed"
        saved = c.post(url).json()["path"]
        assert json.loads((tmp_path / saved).read_text())["dataset_version"] == version
        apply(c, {"input.csv": "id,value\n003,4\n"})
        assert c.get(f"/api/jobs/{job['id']}").json()["recalculation_required"] is True
        assert c.get(url).status_code == 409
        assert c.post(url).status_code == 409


def test_generation_does_not_modify_validator_input(settings):
    observed = []

    def mutating_engine(dataset, config):
        dataset["input.csv"] = "changed"
        return {"result": 1}

    def independent(dataset, plan):
        observed.append(dataset)
        return ValidationReport("passed")

    with TestClient(
        create_app(settings, generator=mutating_engine, validator=independent),
        headers=HEADERS,
    ) as c:
        apply(c)
        assert c.post("/api/jobs", json={}).status_code == 200
    assert observed == [FILES]


def test_validation_failure_and_exception_preserve_previous_result(settings):
    with TestClient(
        create_app(settings, generator=good_plan, validator=passed), headers=HEADERS
    ) as c:
        apply(c)
        good = c.post("/api/jobs", json={}).json()
    bad_report = lambda dataset, plan: ValidationReport(  # noqa: E731
        "failed", [Issue(file="plan.json", row=1, column="x", reason="test violation")]
    )
    with TestClient(
        create_app(settings, generator=good_plan, validator=bad_report), headers=HEADERS
    ) as c:
        assert c.post("/api/jobs", json={}).status_code == 422
        assert c.get(f"/api/jobs/{good['id']}/export").status_code == 200
        failed = c.get("/api/jobs").json()["jobs"][0]
        assert failed["plan"] is None
        assert failed["report"]["status"] == "failed"

    def explode(dataset, config):
        raise RuntimeError("test-only failure")

    with TestClient(
        create_app(settings, generator=explode, validator=passed), headers=HEADERS
    ) as c:
        assert c.post("/api/jobs", json={}).status_code == 500
        assert c.get(f"/api/jobs/{good['id']}/export").status_code == 200


def test_lock_is_shared_between_connections_and_blocks_dataset_apply(client, settings):
    apply(client)
    entered, release = threading.Event(), threading.Event()

    def slow(dataset, config):
        entered.set()
        assert release.wait(5)
        return {}

    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(jobs.run_job, settings, {}, slow, passed)
        try:
            assert entered.wait(5)
            assert client.post("/api/jobs", json={}).status_code == 409
            assert (
                client.post("/api/datasets/apply", json={"files": FILES}).status_code
                == 409
            )
        finally:
            release.set()
        assert future.result()["status"] == "completed"


def test_restart_keeps_lock_and_recovery_requires_matching_id(settings):
    with TestClient(create_app(settings), headers=HEADERS) as c:
        version = apply(c)
    with connection(settings.database_path, write=True) as db:
        db.execute(
            "INSERT INTO jobs(id,dataset_id,status,config_json,created_at) "
            "VALUES ('interrupted',?,'running','{}','test')",
            (version,),
        )
        db.execute("UPDATE runtime_state SET running_job='interrupted'")
    with TestClient(create_app(settings), headers=HEADERS) as c:
        assert c.post("/api/jobs", json={}).status_code == 409
        with pytest.raises(ValueError):
            recover(settings, "wrong-id")
        recover(settings, "interrupted")
        assert c.get("/api/jobs/interrupted").json()["status"] == "failed"
        assert c.post("/api/jobs", json={}).status_code == 501


def test_unknown_ids_and_upload_limit(client, settings):
    assert client.get("/api/jobs/not-found").status_code == 404
    settings.max_upload_bytes = 1
    assert client.post("/api/datasets/apply", json={"files": FILES}).status_code == 413
