# 시험 작업 규칙

목적:

- 원본 `README.md`와 주최 측 양식은 덮어쓰거나 문체 교정하지 않는다. 비밀값은 코드·문서·커밋에 넣지 않는다.
- 우선순위는 응시 README > `docs/DECISION.md`의 확정 기록 > research다. README와 충돌하는 결정은 수정한다.
- `validator/`는 `engine/` 및 생성기의 판정·헬퍼를 가져다 쓰지 않는다. 공통 데이터 계약만 공유한다. 과제 고유 규칙은 README 확인 후 ID를 붙여 추가한다.
- 시작·복귀 시 `docs/INDEX.md`, `docs/DECISION.md`, `docs/STATUS.md`, `docs/TASKS.md`를 읽는다. 새 문서는 INDEX에, 사실·결정·가정은 F/D/A ID로 DECISION에 기록한다.
- 조사는 해결할 질문·결정 ID에 연결하고 15분을 넘기지 않는다. 미해결 사항은 담당자 질문과 가정 후보로 남긴다.
- 데이터 분석 전 `.agents/skills/polars/SKILL.md`와 해당 참조를 읽는다. Python은 Polars `scan_*`·lazy API를 기본으로 하며 버전·형식·결측·키·결과 행 수를 확인한다. 한국어 산문에는 humanizer-ko를 적용하되 사실·수치·인용을 보존한다.
- 합의된 범위는 이어서 구현한다. 메인·검증기·데이터 역할은 필요한 경우 최대 3세션으로 시작한다. 도구를 실제로 쓰지 않았으면 사용했다고 기록하지 않는다.
- 앱을 포함한 경우 설치 `uv sync --locked`, 실행 `uv run --locked python -m uvicorn harness_app.main:app --app-dir app/backend --host 0.0.0.0 --port 8080`, 검사 `uv run --locked pytest`. 문서만 가져왔다면 이 명령을 가용하다고 간주하지 않는다.
- Docker는 실제 과제의 지정 디렉터리에서 사용자가 구성·실행한다. 이 템플릿은 Docker 파일·빌드 성공을 제공하지 않는다.
- 완료는 요구사항 수용 기준 통과와 테스트 성공, 구현된 독립 검증기의 실행·위반 0건으로 판단한다. 미구현·미실행을 성공으로 쓰지 않는다. 중단 전 STATUS와 TASKS를 갱신한다.
