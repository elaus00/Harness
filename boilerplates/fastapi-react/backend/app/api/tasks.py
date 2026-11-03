from datetime import datetime, timezone
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, field_validator

from app.api.auth import require_user
from app.core.database import get_db

router = APIRouter(tags=["workspace"])
Status = Literal["todo", "in_progress", "done"]
Project = Literal["Harness", "제품 디자인", "개발 환경"]
Priority = Literal["high", "medium", "low"]


class TaskInput(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    project: Project = "Harness"
    priority: Priority = "medium"

    @field_validator("title")
    @classmethod
    def valid_title(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("제목을 입력하세요.")
        return value


class TaskUpdate(BaseModel):
    status: Status


def record(db, user_id, message):
    db.execute(
        "INSERT INTO events(user_id,message,created_at) VALUES (?,?,?)",
        (user_id, message, datetime.now(timezone.utc).isoformat()),
    )


@router.get("/workspace")
def workspace(user=Depends(require_user), db=Depends(get_db)):
    tasks = db.execute(
        "SELECT * FROM tasks WHERE user_id=? ORDER BY id DESC", (user.id,)
    )
    events = db.execute(
        "SELECT id,message,created_at FROM events WHERE user_id=? "
        "ORDER BY id DESC LIMIT 8",
        (user.id,),
    )
    return {
        "tasks": [dict(row) for row in tasks],
        "events": [dict(row) for row in events],
    }


@router.post("/tasks", status_code=201)
def create_task(data: TaskInput, user=Depends(require_user), db=Depends(get_db)):
    now = datetime.now(timezone.utc).isoformat()
    cursor = db.execute(
        "INSERT INTO tasks(user_id,title,project,status,priority,created_at) "
        "VALUES (?,?,?,?,?,?)",
        (user.id, data.title, data.project, "todo", data.priority, now),
    )
    record(db, user.id, f"“{data.title}” 업무를 만들었습니다.")
    return dict(
        db.execute("SELECT * FROM tasks WHERE id=?", (cursor.lastrowid,)).fetchone()
    )


@router.patch("/tasks/{task_id}")
def update_task(
    task_id: int, data: TaskUpdate, user=Depends(require_user), db=Depends(get_db)
):
    task = db.execute(
        "SELECT * FROM tasks WHERE id=? AND user_id=?", (task_id, user.id)
    ).fetchone()
    if not task:
        raise HTTPException(404, "업무를 찾을 수 없습니다.")
    db.execute(
        "UPDATE tasks SET status=? WHERE id=? AND user_id=?",
        (data.status, task_id, user.id),
    )
    label = {"todo": "해야 할 일", "in_progress": "진행 중", "done": "완료"}[
        data.status
    ]
    record(db, user.id, f"“{task['title']}” → {label}")
    return {"id": task_id, "status": data.status}


@router.post("/tasks/sample", status_code=201)
def sample(user=Depends(require_user), db=Depends(get_db)):
    db.execute("BEGIN IMMEDIATE")
    if db.execute("SELECT 1 FROM tasks WHERE user_id=?", (user.id,)).fetchone():
        raise HTTPException(
            409, "샘플은 업무가 없는 워크스페이스에만 추가할 수 있습니다."
        )
    examples = [
        ("프로젝트 작업 규칙 정리", "Harness", "done", "high"),
        ("API 응답 형식과 오류 처리 정의", "개발 환경", "in_progress", "high"),
        ("대시보드 컴포넌트 정리", "제품 디자인", "in_progress", "medium"),
        ("첫 번째 사용자 흐름 검증", "Harness", "todo", "high"),
        ("컬러와 간격 토큰 점검", "제품 디자인", "done", "medium"),
        ("개발 환경 설치 안내 작성", "개발 환경", "done", "low"),
        ("세션 회고 워크플로우 개선", "Harness", "todo", "medium"),
    ]
    now = datetime.now(timezone.utc).isoformat()
    db.executemany(
        "INSERT INTO tasks(user_id,title,project,status,priority,created_at) "
        "VALUES (?,?,?,?,?,?)",
        [
            (user.id, title, project, status, priority, now)
            for title, project, status, priority in examples
        ],
    )
    record(db, user.id, "시작을 위한 샘플 업무 7개를 추가했습니다.")
    return {"created": len(examples)}
