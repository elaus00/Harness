import csv
import io
import json
import uuid
from datetime import datetime, timezone
from pathlib import PurePosixPath

import polars as pl
from pydantic import BaseModel, Field

from contracts import Issue

from .database import connection
from .errors import Fault


def now():
    return datetime.now(timezone.utc).isoformat()


class DatasetInput(BaseModel):
    files: dict[str, str] = Field(min_length=1, max_length=100)


def profile(files, max_bytes):
    if sum(len(text.encode("utf-8")) for text in files.values()) > max_bytes:
        raise Fault(413, "dataset_too_large", "데이터셋 크기 제한을 초과했습니다.")
    profiles = {}
    for name, text in files.items():
        if (
            PurePosixPath(name).name != name
            or "\\" in name
            or not name
            or not name.lower().endswith(".csv")
        ):
            raise Fault(
                422,
                "invalid_filename",
                "CSV 파일명을 확인하세요.",
                issues=[Issue(file=name, reason="경로 없는 CSV 파일명이 필요합니다.")],
            )
        try:
            header = next(csv.reader(io.StringIO(text.lstrip("\ufeff")), strict=True))
            if (
                not header
                or any(not h for h in header)
                or len(set(header)) != len(header)
            ):
                raise Fault(
                    422,
                    "csv_header",
                    "헤더를 확인하세요.",
                    issues=[
                        Issue(
                            file=name,
                            row=1,
                            reason="헤더는 비어 있지 않은 고유 이름이어야 합니다.",
                        )
                    ],
                )
            scan = pl.scan_csv(io.BytesIO(text.encode("utf-8")), infer_schema=False)
            schema = scan.collect_schema()
            stats = (
                scan.select(
                    pl.len().alias("row_count"),
                    pl.all().null_count().name.prefix("null:"),
                )
                .collect(engine="streaming")
                .row(0, named=True)
            )
            profiles[name] = {
                "rows": stats["row_count"],
                "columns": list(schema),
                "dtypes": {key: str(value) for key, value in schema.items()},
                "nulls": {key: stats["null:" + key] for key in schema},
            }
        except (pl.exceptions.PolarsError, csv.Error, StopIteration) as exc:
            raise Fault(
                422,
                "csv_parse_error",
                "CSV를 읽을 수 없습니다.",
                issues=[
                    Issue(file=name, reason=f"CSV 구문 오류 ({type(exc).__name__})")
                ],
            ) from exc
    return {"scope": "csv_syntax_only", "domain_checked": False, "files": profiles}


def apply_dataset(settings, files):
    summary = profile(files, settings.max_upload_bytes)
    version = uuid.uuid4().hex
    with connection(settings.database_path, write=True) as db:
        state = db.execute("SELECT * FROM runtime_state WHERE id=1").fetchone()
        if state["running_job"]:
            raise Fault(
                409, "job_running", "생성 중에는 데이터셋을 적용할 수 없습니다."
            )
        db.execute(
            "INSERT INTO datasets VALUES (?,?,?,?)",
            (
                version,
                json.dumps(files, ensure_ascii=False),
                json.dumps(summary, ensure_ascii=False),
                now(),
            ),
        )
        db.execute("UPDATE runtime_state SET active_dataset=? WHERE id=1", (version,))
    return {"version": version, "profile": summary}


def list_datasets(settings):
    with connection(settings.database_path) as db:
        active = db.execute("SELECT active_dataset FROM runtime_state").fetchone()[0]
        rows = db.execute(
            "SELECT id,profile_json,created_at FROM datasets ORDER BY created_at DESC"
        ).fetchall()
    return {
        "active_version": active,
        "datasets": [
            {
                "version": row["id"],
                "profile": json.loads(row["profile_json"]),
                "created_at": row["created_at"],
            }
            for row in rows
        ],
    }
