"""Manual recovery only after all generator processes have been stopped."""

import argparse
import json

from .config import Settings
from .database import connection


def recover(settings, job_id):
    with connection(settings.database_path, write=True) as db:
        current = db.execute("SELECT running_job FROM runtime_state").fetchone()[0]
        if current != job_id:
            raise ValueError("현재 실행 잠금의 작업 ID와 일치하지 않습니다.")
        db.execute(
            "UPDATE jobs SET status='failed',error_json=? "
            "WHERE id=? AND status='running'",
            (
                json.dumps(
                    {
                        "code": "manually_recovered",
                        "reason": "프로세스 중단 확인 후 수동 복구",
                    }
                ),
                job_id,
            ),
        )
        db.execute("UPDATE runtime_state SET running_job=NULL WHERE id=1")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("job_id")
    parser.add_argument("--processes-stopped", action="store_true", required=True)
    args = parser.parse_args()
    recover(Settings(), args.job_id)
    print("중단 작업을 실패로 기록하고 잠금을 해제했습니다.")


if __name__ == "__main__":
    main()
