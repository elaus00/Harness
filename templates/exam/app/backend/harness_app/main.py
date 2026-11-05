import json
import logging
import os
import secrets
import sqlite3
import tempfile
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pwdlib import PasswordHash
from starlette.exceptions import HTTPException

from contracts import Issue
from engine import generate
from validator import validate

from . import auth, datasets, jobs
from .config import Settings
from .database import connection, initialize, readiness
from .errors import Fault, error_response

FRONTEND = Path(__file__).resolve().parents[2] / "frontend"
logger = logging.getLogger(__name__)


def create_app(settings=None, *, generator=generate, validator=validate):
    config = settings or Settings()
    passwords = PasswordHash.recommended()

    @asynccontextmanager
    async def lifespan(app):
        initialize(config, passwords)
        readiness(config.database_path)
        yield

    app = FastAPI(title="Exam Harness", lifespan=lifespan)
    app.state.settings = config
    app.state.passwords = passwords
    app.state.dummy_hash = passwords.hash(secrets.token_urlsafe(32))

    @app.exception_handler(Fault)
    async def handle_fault(request, exc):
        return error_response(exc.status, exc.code, exc.issues)

    @app.exception_handler(HTTPException)
    async def handle_http(request, exc):
        return error_response(
            exc.status_code, "http_error", [Issue(reason=str(exc.detail))], exc.headers
        )

    @app.exception_handler(RequestValidationError)
    async def handle_input(request, exc):
        issues = [
            Issue(reason=error["msg"], column=".".join(map(str, error["loc"])))
            for error in exc.errors()
        ]
        return error_response(422, "request_validation", issues)

    @app.exception_handler(sqlite3.Error)
    async def handle_database(request, exc):
        logger.error("Database unavailable: %s", type(exc).__name__)
        return error_response(
            503,
            "database_unavailable",
            [Issue(reason="데이터베이스 상태를 확인하세요.")],
        )

    @app.exception_handler(Exception)
    async def handle_unexpected(request, exc):
        logger.error("Request failed: %s", type(exc).__name__)
        return error_response(
            500,
            "internal_error",
            [Issue(reason="요청 처리에 실패했습니다. 서버 상태를 확인하세요.")],
        )

    @app.middleware("http")
    async def request_guard(request, call_next):
        if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
            origin = request.headers.get("origin")
            if request.headers.get("x-requested-with") != "Harness" or (
                origin is not None and origin not in config.allowed_origins
            ):
                return error_response(
                    403,
                    "origin_rejected",
                    [Issue(reason="허용되지 않은 요청 출처입니다.")],
                )
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Cache-Control"] = "no-store"
        return response

    @app.get("/api/health")
    def health():
        readiness(config.database_path)
        return {"status": "ok", "database": "ready"}

    @app.get("/api/config")
    def configuration():
        return {
            "auth_enabled": config.auth_enabled,
            "workflow_enabled": config.workflow_enabled,
        }

    app.post("/api/auth/login")(auth.login)
    app.post("/api/auth/logout")(auth.logout)

    @app.get("/api/auth/me")
    def me(user=Depends(auth.current_user)):
        return {
            **user,
            "can_write": (
                not config.auth_enabled or user["role"] in config.write_roles
            ),
        }

    def workflow():
        if not config.workflow_enabled:
            raise Fault(404, "workflow_disabled", "생성형 과제 기능이 꺼져 있습니다.")

    @app.get("/api/datasets", dependencies=[Depends(workflow)])
    def dataset_list(user=Depends(auth.current_user)):
        return datasets.list_datasets(config)

    @app.post("/api/datasets/validate", dependencies=[Depends(workflow)])
    def dataset_validate(data: datasets.DatasetInput, user=Depends(auth.write_user)):
        return datasets.profile(data.files, config.max_upload_bytes)

    @app.post("/api/datasets/apply", dependencies=[Depends(workflow)])
    def dataset_apply(data: datasets.DatasetInput, user=Depends(auth.write_user)):
        return datasets.apply_dataset(config, data.files)

    @app.get("/api/jobs", dependencies=[Depends(workflow)])
    def job_list(user=Depends(auth.current_user)):
        with connection(config.database_path) as db:
            ids = [
                r[0] for r in db.execute("SELECT id FROM jobs ORDER BY created_at DESC")
            ]
        return {"jobs": [jobs.get_job(config, job_id) for job_id in ids]}

    @app.post("/api/jobs", dependencies=[Depends(workflow)])
    def job_create(options: dict[str, Any], user=Depends(auth.write_user)):
        return jobs.run_job(config, options, generator, validator)

    @app.get("/api/jobs/{job_id}", dependencies=[Depends(workflow)])
    def job_get(job_id: str, user=Depends(auth.current_user)):
        return jobs.get_job(config, job_id)

    @app.get("/api/jobs/{job_id}/export", dependencies=[Depends(workflow)])
    def job_export(job_id: str, user=Depends(auth.current_user)):
        return jobs.export_job(config, job_id)

    @app.post("/api/jobs/{job_id}/export", dependencies=[Depends(workflow)])
    def job_save(job_id: str, user=Depends(auth.write_user)):
        # Serialize against dataset application; never save a stale version as current.
        with connection(config.database_path, write=True):
            result = jobs.export_job(config, job_id)
            output = Path("output")
            output.mkdir(exist_ok=True)
            destination = output / (result["id"] + ".json")
            temp_path = None
            try:
                with tempfile.NamedTemporaryFile(
                    mode="w", encoding="utf-8", dir=output, delete=False
                ) as stream:
                    temp_path = Path(stream.name)
                    json.dump(
                        result, stream, ensure_ascii=False, indent=2, allow_nan=False
                    )
                os.replace(temp_path, destination)
            finally:
                if temp_path and temp_path.exists():
                    temp_path.unlink()
        return {"path": str(destination), "dataset_version": result["dataset_version"]}

    @app.get("/", include_in_schema=False)
    def index():
        return FileResponse(FRONTEND / "index.html")

    app.mount("/assets", StaticFiles(directory=FRONTEND), name="assets")
    return app


app = create_app()
