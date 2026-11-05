# Harness

개인 작업 방식을 문서와 스킬로 관리하고, 새 프로젝트에서 재사용하는 개발 기반입니다. FastAPI · React · Vite 보일러플레이트에 기본 인증과 Jira 스타일 대시보드가 포함되어 있습니다.

## 주요 기능

- **작업 Harness**: `AGENTS.md`, 문서 색인, 작업 계획·결정·교훈 기록과 세션 인계.
- **프로젝트 템플릿**: 적용 전 미리보기, 기존 파일 보존, 회고 스킬 복사.
- **인증**: 이메일·비밀번호 가입/로그인, Argon2 비밀번호 해시, HttpOnly 쿠키 세션, 만료·로그아웃.
- **대시보드**: 프로젝트 요약, 업무 생성·상태 변경·검색·필터, 최근 활동, 모바일 메뉴.
- **저장**: SQLite를 이용한 사용자별 계정·세션·업무·활동 보존.
- **디자인**: Atlassian 공식 디자인 토큰과 공통 React UI 컴포넌트.
- **Docker**: FastAPI와 Nginx 정적 웹 이미지를 Compose로 실행하고 같은 출처에서 API 연결.

상세 실행 절차는 [HOW_TO_RUN](How_to_run.md)을 참고하세요.

## Docker로 빠르게 시작

Docker Engine/Desktop과 Docker Compose 2.20 이상이 필요합니다. 다음 명령은 저장소 루트에서 실행합니다.

```sh
git clone https://github.com/elaus00/Harness.git
cd Harness
docker compose up --build -d --wait
```

- 대시보드: [http://127.0.0.1:8080](http://127.0.0.1:8080)
- API 문서: [http://127.0.0.1:8080/docs](http://127.0.0.1:8080/docs)
- 상태 확인: [http://127.0.0.1:8080/api/v1/health](http://127.0.0.1:8080/api/v1/health)

첫 방문 시 회원가입하세요. 기본 계정은 없습니다. 가입 후 업무를 직접 만들거나 **샘플 업무 불러오기**로 예시 7개를 추가할 수 있습니다. 저장소가 비공개이면 clone 전에 GitHub 인증이 필요합니다.

```sh
# 이미지 빌드만 확인
docker compose build

# 서비스와 로그 확인
docker compose ps
docker compose logs -f

# 종료: SQLite 데이터 볼륨은 유지
docker compose down
```

SQLite는 `harness-data` 이름의 Compose 볼륨에 저장됩니다. `docker compose down -v`는 계정과 업무 데이터도 삭제합니다.

8080 포트를 변경하면 허용 Origin도 함께 변경합니다.

```sh
HARNESS_PORT=8081 \
HARNESS_ALLOWED_ORIGINS='["http://127.0.0.1:8081","http://localhost:8081"]' \
docker compose up --build -d --wait
```

## 로컬 개발

Node.js 22.12 이상, npm, uv, make가 필요합니다. 백엔드는 Python 3.12를 사용합니다.

```sh
cd boilerplates/fastapi-react
make install
```

터미널 두 개에서 각각 실행합니다.

```sh
make backend
```

```sh
make frontend
```

기본 화면은 [http://127.0.0.1:5173](http://127.0.0.1:5173), API는 [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)입니다. 포트 변경과 상세 설정은 [보일러플레이트 실행 안내](boilerplates/fastapi-react/README.md)를 참고하세요.

## 검증

```sh
# 저장소 루트: 템플릿 적용 도구 검증
python3 -m unittest discover -s tests -v

# 앱: lint, API 테스트, TypeScript 검사, 프로덕션 빌드
cd boilerplates/fastapi-react
make check

# 실제 서버의 HTTP 연결 확인
make smoke

# 실제 브라우저에서 인증·업무·모바일 흐름 확인
cd frontend
npx playwright install chromium
cd ..
make e2e
```

의존성은 `backend/uv.lock`과 `frontend/package-lock.json`에 기록합니다. Docker 백엔드는 개발 의존성을 제외하고, 프론트엔드는 멀티 스테이지 빌드로 생성한 정적 파일을 Nginx에서 제공합니다.

## 구조

```text
.
├── AGENTS.md                         # 공통 작업 규칙
├── compose.yaml                      # 루트 Docker 실행 진입점
├── .agents/skills/clear-with-lessons/ # 세션 회고·인계 스킬
├── docs/                             # 색인·계획·결정·교훈·현재 상태
├── templates/project/                # 프로젝트별 문서 템플릿
├── scripts/apply.py                  # 미리보기 및 기존 파일 보존 적용
├── tests/                            # 적용 도구 검증
└── boilerplates/fastapi-react/
    ├── compose.yaml                  # 독립적으로 재사용할 앱 구성
    ├── backend/                      # FastAPI·SQLite·인증·업무 API
    ├── frontend/                     # React·TypeScript·Vite·Nginx
    ├── scripts/smoke.py               # HTTP 통합 확인
    └── DESIGN_SYSTEM.md              # 디자인 토큰과 공통 UI 규칙
```

## 기존 프로젝트에 Harness 적용

대상 폴더가 먼저 존재해야 합니다. 저장소 루트에서 실행합니다.

```sh
python3 scripts/apply.py "/절대/경로/프로젝트"
python3 scripts/apply.py "/절대/경로/프로젝트" --apply
```

첫 명령은 미리보기입니다. `--apply`는 신규 파일만 추가하고 기존 파일은 보존합니다. 이미 존재하는 `AGENTS.md`와 문서 색인은 출력 안내에 따라 검토 후 병합하세요. 회고 스킬은 대상 프로젝트의 `.agents/skills/clear-with-lessons`에 복사합니다.

`brainstorming`과 Impeccable 등 외부 스킬의 설치 현황은 `skills-lock.json`과 [도구 안내](docs/tools.md)에 기록되어 있습니다. 로컬 설치 기록은 다른 컴퓨터의 설치·인증 상태를 자동 복원하지 않습니다.

## 설정과 운영 범위

- 로컬 설정 예시는 `backend/.env.example`, `frontend/.env.example`을 참고하세요.
- Docker는 `.env`, 로컬 데이터베이스, 설치 폴더, 테스트 결과를 이미지에 포함하지 않습니다.
- 기본 Compose는 로컬 HTTP 확인용으로 `127.0.0.1:8080`에만 노출됩니다.
- HTTPS 운영 환경에서는 TLS reverse proxy, `HARNESS_COOKIE_SECURE=true`, 실제 `HARNESS_ALLOWED_ORIGINS`를 설정하세요.
- SQLite는 기본 단일 인스턴스 저장 구성입니다. 팀 운영에는 DB 마이그레이션·백업·권한 정책과 공유 rate limit을 함께 설계해야 합니다.
- 이메일 소유권 확인, 비밀번호 재설정, 소셜 로그인, 팀 권한과 Jira API 연동은 포함되어 있지 않습니다.

## 문서

- [문서 색인](docs/index.md)
- [현재 상태와 검증 기록](docs/status.md)
- [작업 흐름](docs/workflow.md)
- [앱 실행·인증·저장](boilerplates/fastapi-react/README.md)
- [디자인 시스템](boilerplates/fastapi-react/DESIGN_SYSTEM.md)

## 참고

- [FastAPI](https://fastapi.tiangolo.com/)
- [Vite](https://vite.dev/guide/)
- [Atlassian Design System](https://atlassian.design/)
- [uv Docker 가이드](https://docs.astral.sh/uv/guides/integration/docker/)
- [Docker Compose](https://docs.docker.com/compose/)
