# 기반 파일 사용법

이 문서는 문제와 무관한 연결부의 사용법이다. 과제 목적·입출력·도메인 규칙은 현장에서 PRD와 DECISION에 기록한다. 주최 측 README·양식은 원래 경로에 보존한다.

## 가져오기

Harness는 별도 보관 폴더에 clone한다. 그 폴더에서 대상 디렉터리가 존재하는지 확인하고 아래 중 필요한 명령을 실행한다. 미리보기 후 `--apply`를 붙이면 적용한다.

```sh
# 시험 문서와 모든 동봉 스킬
python3 scripts/apply.py /path/to/exam-project --profile docs

# 문서·스킬과 선택적 앱 연결부
python3 scripts/apply.py /path/to/exam-project --profile exam

# 스킬만 설치
python3 scripts/apply.py /path/to/exam-project --skills-only --apply
```

전체 디렉터리를 덮어쓰지 않는다. exam·docs 프로필은 다른 내용의 기존 파일이나 대소문자·심링크 충돌을 발견하면 쓰기 전에 중단한다. 같은 파일은 건너뛰고 기존 스킬은 폴더 전체를 보존한다. 기존 AGENTS·문서가 있다면 별도 빈 준비 폴더에 추출한 뒤 필요한 내용만 검토·병합한다. 이 도구는 자동 병합이나 업데이트 도구가 아니다.

이 문서가 docs 프로필로만 복사됐다면 아래 앱 명령을 실행할 코드·의존성은 없다. 앱은 exam 프로필 또는 수동 선택으로 가져올 수 있다. Docker 파일은 어느 프로필에도 포함되지 않는다.

## 앱 실행

앱을 추출한 **대상 프로젝트 루트**에서 Python 3.12와 uv를 사용한다. FastAPI가 정적 프론트엔드와 상대 경로 API를 함께 제공하므로 Node·별도 프론트 빌드가 필요 없다. 최초 의존성 설치에는 패키지 저장소 접근이 필요하다.

```sh
uv sync --locked
cp .env.example .env
uv run --locked python -m uvicorn harness_app.main:app --app-dir app/backend --host 0.0.0.0 --port 8080
```

웹 IDE에서 8080 포트를 미리보기로 연다. 다른 포트는 실행 명령에서 지정한다. 브라우저가 접속하는 실제 Origin(스킴·호스트·포트, 경로 제외)을 `.env`의 `HARNESS_ALLOWED_ORIGINS` JSON 배열에 넣는다. HTTPS 미리보기에서 인증을 쓰면 `HARNESS_COOKIE_SECURE=true`로 설정한다. 설정 변경 후 앱을 재시작한다. 기본 로컬 주소는 `http://127.0.0.1:8080`이다.

Docker 구성과 빌드·실행은 실제 과제의 요구에 맞춰 사용자가 지정 디렉터리에서 별도로 수행한다. 하네스에는 Docker 성공을 완료 조건으로 두지 않는다.

## 설정과 인증

| 설정 | 기본·의미 |
| --- | --- |
| HARNESS_DATABASE_PATH | `data/harness.sqlite3`; 시작 시 스키마·WAL 준비 |
| HARNESS_AUTH_ENABLED | false; 인증은 선택 사항. false이면 읽기·쓰기 API에 로그인 요구 없음 |
| HARNESS_ACCOUNTS | 인증 사용 시 역할이 다른 계정 두 개를 지정하는 JSON 배열 |
| HARNESS_WRITE_ROLES | 인증 사용 시 쓰기를 허용할 역할 이름의 JSON 배열 |
| HARNESS_COOKIE_SECURE | false; HTTPS 인증 환경에서 true |
| HARNESS_SESSION_HOURS | 8; 세션 유효 시간 |
| HARNESS_ALLOWED_ORIGINS | 허용할 브라우저 Origin의 JSON 배열 |
| HARNESS_WORKFLOW_ENABLED | false; 데이터셋·생성·Export API와 화면 활성화 여부 |
| HARNESS_MAX_UPLOAD_BYTES | 10485760; 데이터셋 UTF-8 본문 총 크기 제한. 도메인 규칙이 아닌 메모리 사용 상한 |

계정 항목의 필드는 `username`, `role`, `password`이며 각 비밀번호는 12자 이상이다. 역할명과 쓰기 권한은 현장 README에 맞춰 정하고 비밀번호는 환경변수·커밋하지 않는 .env로 제공한다. 인증을 켠 상태에서 계정·권한이 빠지면 설정 이름을 포함하는 오류로 시작을 중단한다. `HARNESS_ACCOUNTS=[]` 예시는 실사용 계정이 아니다.

시작 시 두 계정을 생성·동기화한다. 동일 비밀번호는 유지하고 비밀번호·역할이 바뀐 계정의 세션은 폐기한다. 설정에서 빠진 계정은 비활성화한다. 업무·데이터셋은 지우지 않는다. 쓰기 권한은 서버에서 검사하며 클라이언트의 역할 헤더를 신뢰하지 않는다.

이 인증은 시험용 연결부다. 비밀번호 재설정·외부 SSO·다중 조직·공개 서비스 운영 정책을 제공하지 않는다. 해당 기능을 요구하면 과제 범위에서 추가한다.

## 생성형 과제의 연결부

`HARNESS_WORKFLOW_ENABLED=true`로 켠다. 프론트는 CSV 파일 선택·구문 확인·새 버전 적용·생성·작업 조회·화면 결과·복사·서버 저장을 제공한다.

- 데이터셋 요청은 `files: {파일명: 원본 CSV 문자열}`이다. CSV는 UTF-8·쉼표·고유한 비어 있지 않은 헤더를 받는다. 다른 인코딩·구분자·멀티 파일 계약은 현장에 맞게 변경한다.
- Polars 1.x lazy scan을 사용하고 셀은 문자열로 유지한다. 선행 0, 원본 문자열, 결측을 임의로 숫자·날짜로 변환하지 않는다. 프로파일은 행 수·열·자료형·결측 수다.
- 구문 검사 응답은 `scope=csv_syntax_only`, `domain_checked=false`다. 키·참조·범위·용량 등 과제 제약 검증을 대신하지 않는다. 현장 데이터 적용 전에 해당 검사를 추가한다.
- 적용 시 새 UUID 버전과 원문을 SQLite에 함께 저장하고 활성 버전을 같은 트랜잭션에서 바꾼다. 실패 시 기존 버전이 유지된다. 생성 중에는 적용이 차단된다.
- `engine.generate(dataset, settings)`는 JSON 객체 계획을, `validator.validate(dataset, plan)`은 `contracts.ValidationReport`를 반환한다. 둘 다 기본적으로 NotImplementedError이며 도메인 로직은 없다.
- 생성·검증에 서로 다른 원본 복사본을 전달한다. validator는 engine과 앱 코드를 가져다 쓰지 않는다. 명시적 passed 보고서가 있어야 결과를 완료로 게시한다. 미구현은 HTTP 501이며 검증 위반·실패는 결과로 게시하지 않는다.
- 생성 잠금은 SQLite에 저장되어 프로세스 간 공유된다. 결과에는 데이터셋 버전·설정·검증 보고서를 연결한다. 활성 버전이 바뀐 과거 결과는 재계산 필요로 표시하고 Export를 막는다.
- 서버 저장은 작업 ID 기반 `output/<id>.json`에 원자적으로 기록한다. 이는 중립적인 결과 봉투이며 현장 Export 스키마와 동일하다고 간주하지 않는다.
- 데이터셋은 크기 제한 내 원문을 DB·요청 메모리에 보관한다. 대용량용 파일 저장소·백그라운드 작업 큐는 포함하지 않는다. 생성 요청은 동기 처리이므로 장시간 작업의 IDE 프록시 제한은 현장에서 확인한다.

## API와 오류

| 경로 | 동작 |
| --- | --- |
| GET /api/health | 실제 DB·필수 스키마 준비 확인. 실패 시 503 |
| GET /api/config | 선택 기능 활성 여부 |
| POST /api/auth/login, /logout | 로그인·세션 폐기 |
| GET /api/auth/me | 사용자·역할·쓰기 가능 여부 |
| GET /api/datasets | 버전 목록·활성 버전 |
| POST /api/datasets/validate, /apply | CSV 구문 확인 / 새 버전 적용 |
| POST /api/jobs | 설정 JSON으로 생성·독립 검증 |
| GET /api/jobs, /api/jobs/{id} | 작업 목록·결과·재계산 필요 표시 |
| GET /api/jobs/{id}/export | 검증 완료·최신 버전 결과의 화면 표시·복사 |
| POST /api/jobs/{id}/export | 같은 결과의 서버 저장 |

변경 요청은 `X-Requested-With: Harness` 헤더를 사용한다. 오류는 `error.code`와 `error.issues` 배열이며 각 항목은 `file`, `row`, `column`, `reason`, 선택적 `rule_id`다. 모르는 위치는 null이고 행 번호는 알 때 1부터 센다. Polars 구문 오류의 정확한 행·열을 모르면 추측해 채우지 않는다.

## 검증과 복구

```sh
uv run --locked ruff check .
uv run --locked pytest
uv run --locked python scripts/check_boundaries.py
```

템플릿 테스트의 생성기·검증기 성공 구현은 테스트용 스텁이다. 실제 과제 검증 성공을 뜻하지 않는다. 정적 import 검사만으로 동적·간접 의존성 전체를 증명할 수 없으므로 validator 코드도 검토한다.

강제 종료된 작업의 잠금은 재시작해도 자동 해제하지 않는다. 다른 프로세스가 여전히 실행할 수 있기 때문이다. 모든 관련 생성 프로세스를 먼저 종료하고, 실제 잠금의 작업 ID를 확인한 뒤에만 실행한다.

```sh
PYTHONPATH=app/backend uv run --locked python -m harness_app.recover WORK_ID --processes-stopped
```

이 명령은 지정 ID가 현재 잠금과 다르면 중단한다. 복구는 작업을 실패로 기록하고 잠금을 해제하며 이전 성공 결과·데이터셋을 지우지 않는다. 실제 현장 실행·검증 결과는 STATUS와 HOW_TO_RUN에 별도로 기록한다.
