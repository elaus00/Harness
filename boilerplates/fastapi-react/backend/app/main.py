from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api import auth, tasks
from app.api.health import router as health_router
from app.core.config import Settings
from app.core.database import SCHEMA, connection


def create_app(settings: Settings | None = None) -> FastAPI:
    config = settings or Settings()

    @asynccontextmanager
    async def lifespan(app):
        config.database_path.parent.mkdir(parents=True, exist_ok=True)
        with connection(config.database_path) as db:
            db.executescript(SCHEMA)
        yield

    app = FastAPI(title="Harness API", version="0.2.0", lifespan=lifespan)
    app.state.settings = config

    @app.middleware("http")
    async def security_headers(request: Request, call_next):
        if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
            origin = request.headers.get("origin")
            if request.headers.get("x-requested-with") != "Harness" or (
                origin is not None and origin not in config.allowed_origins
            ):
                return JSONResponse(
                    {"detail": "허용되지 않은 요청입니다."}, status_code=403
                )
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Cache-Control"] = "no-store"
        return response

    app.include_router(health_router, prefix="/api/v1")
    app.include_router(auth.router, prefix="/api/v1")
    app.include_router(tasks.router, prefix="/api/v1")
    return app


app = create_app()
