import json
import logging
import uuid
from dataclasses import asdict

from contracts import ValidationReport

from .database import connection
from .datasets import now
from .errors import Fault

logger = logging.getLogger(__name__)


def run_job(settings, config, generate, validate):
    job_id = uuid.uuid4().hex
    with connection(settings.database_path, write=True) as db:
        state = db.execute("SELECT * FROM runtime_state WHERE id=1").fetchone()
        if state["running_job"]:
            raise Fault(409, "job_running", "다른 생성 작업이 실행 중입니다.")
        if not state["active_dataset"]:
            raise Fault(409, "dataset_required", "먼저 데이터셋을 적용하세요.")
        dataset = db.execute(
            "SELECT * FROM datasets WHERE id=?", (state["active_dataset"],)
        ).fetchone()
        db.execute(
            "INSERT INTO jobs(id,dataset_id,status,config_json,created_at) "
            "VALUES (?,?,'running',?,?)",
            (
                job_id,
                dataset["id"],
                json.dumps(config, allow_nan=False),
                now(),
            ),
        )
        db.execute("UPDATE runtime_state SET running_job=? WHERE id=1", (job_id,))
    report = None
    try:
        # Separate copies prevent an engine mutating the validator's original input.
        plan = generate(json.loads(dataset["files_json"]), config)
        if not isinstance(plan, dict):
            raise TypeError("Plan must be a JSON object")
        plan_json = json.dumps(plan, ensure_ascii=False, allow_nan=False)
        report = validate(json.loads(dataset["files_json"]), json.loads(plan_json))
        if not isinstance(report, ValidationReport):
            raise TypeError("Validator must return ValidationReport")
        if report.status == "not_implemented":
            raise NotImplementedError("Validator is not implemented")
        if report.status != "passed":
            raise Fault(
                422,
                "plan_invalid",
                "검증에서 위반을 발견했습니다.",
                issues=report.issues,
            )
        report_json = json.dumps(asdict(report), ensure_ascii=False, allow_nan=False)
        with connection(settings.database_path, write=True) as db:
            lock = db.execute("SELECT running_job FROM runtime_state").fetchone()[0]
            if lock != job_id:
                raise Fault(409, "lock_changed", "생성 잠금이 변경됐습니다.")
            db.execute(
                "UPDATE jobs SET status='completed',plan_json=?,report_json=? "
                "WHERE id=?",
                (plan_json, report_json, job_id),
            )
            db.execute("UPDATE runtime_state SET running_job=NULL WHERE id=1")
    except Exception as exc:
        if isinstance(exc, NotImplementedError):
            failure = Fault(
                501, "not_implemented", "현장 생성기·검증기 구현이 필요합니다."
            )
        elif isinstance(exc, Fault):
            failure = exc
        else:
            logger.error("Generation failed: %s", type(exc).__name__)
            failure = Fault(
                500, "generation_failed", "생성에 실패했습니다. 기존 결과는 유지됩니다."
            )
        with connection(settings.database_path, write=True) as db:
            db.execute(
                "UPDATE jobs SET status='failed',error_json=?,report_json=? "
                "WHERE id=? AND status='running'",
                (
                    json.dumps(
                        {
                            "code": failure.code,
                            "issues": [asdict(i) for i in failure.issues],
                        },
                        ensure_ascii=False,
                    ),
                    json.dumps(asdict(report), ensure_ascii=False) if report else None,
                    job_id,
                ),
            )
            db.execute(
                "UPDATE runtime_state SET running_job=NULL WHERE running_job=?",
                (job_id,),
            )
        raise failure from exc
    return get_job(settings, job_id)


def get_job(settings, job_id):
    with connection(settings.database_path) as db:
        row = db.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
        active = db.execute("SELECT active_dataset FROM runtime_state").fetchone()[0]
    if not row:
        raise Fault(404, "job_not_found", "작업을 찾을 수 없습니다.")
    return {
        "id": row["id"],
        "dataset_version": row["dataset_id"],
        "status": row["status"],
        "recalculation_required": active != row["dataset_id"],
        "config": json.loads(row["config_json"]),
        "plan": json.loads(row["plan_json"]) if row["plan_json"] else None,
        "report": json.loads(row["report_json"]) if row["report_json"] else None,
        "error": json.loads(row["error_json"]) if row["error_json"] else None,
    }


def export_job(settings, job_id):
    result = get_job(settings, job_id)
    if result["status"] != "completed" or result["recalculation_required"]:
        raise Fault(
            409, "export_not_ready", "검증 완료된 현재 데이터셋의 결과가 필요합니다."
        )
    return result
