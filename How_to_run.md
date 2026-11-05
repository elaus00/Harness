# HOW_TO_RUN

## 1. 목적과 범위

Harness는 개인 작업 방식을 문서·스킬·템플릿으로 관리하고, 새 프로젝트에서 재사용하기 위한 개발 기반입니다. 반복되는 프로젝트 설정과 세션 인계 작업을 줄이고, 실행 가능한 웹 애플리케이션의 출발점을 제공합니다.

포함된 범위:

- `AGENTS.md`, 문서 색인, 계획·결정·교훈 기록과 세션 회고 스킬.
- 기존 파일을 보존하며 공통 문서와 스킬을 적용하는 프로젝트 템플릿 도구.
- 이메일·비밀번호 회원가입, 로그인, 세션 유지·만료·로그아웃.
- 프로젝트 요약, 업무 생성·상태 변경·검색·필터·최근 활동을 제공하는 개인 대시보드.
- Jira 스타일의 화면과 Atlassian 디자인 토큰 기반 공통 UI.
- SQLite 저장, Docker 이미지 빌드와 Compose 실행.

이메일 소유권 확인, 비밀번호 재설정, 소셜 로그인, 팀별 권한, 프로젝트 생성·삭제, 실제 Jira API 연동, 운영 서버 배포 자동화는 포함하지 않습니다. 기본 프로젝트 분류는 Harness·제품 디자인·개발 환경의 세 가지입니다.

## 2. 기술 스택

| 구분 | 사용 기술 |
| --- | --- |
| 백엔드 | Python 3.12, FastAPI, Uvicorn, Pydantic·pydantic-settings |
| 인증 | pwdlib·Argon2 비밀번호 해시, HttpOnly·SameSite=Lax 세션 쿠키, 서버 측 세션 저장 |
| 저장소 | SQLite, Python 표준 `sqlite3` |
| 프론트엔드 | React 19, TypeScript, Vite 8, Lucide 아이콘 |
| 디자인 | `@atlaskit/tokens`, 로컬 공통 React 컴포넌트와 CSS |
| 의존성 관리 | uv·`uv.lock`, npm·`package-lock.json` |
| 컨테이너 | Docker, Docker Compose, Python 3.12·Node 24 빌드 이미지, Nginx 1.28 |
| 검증 | unittest, pytest, Ruff, Oxlint, TypeScript, Playwright |
| 코드 보관 | GitHub 비공개 저장소 `elaus00/Harness` |

앱의 기본 실행에는 외부 인증·DB 서비스나 API 키가 필요하지 않습니다. Context7 등 연결 도구와 개인 Codex 스킬은 개발 보조 도구이며 웹 앱 실행과 별개입니다.

## 3. 준비 사항

### Docker로 실행할 경우

- Git 또는 저장소 소스 파일을 준비합니다. 비공개 저장소를 clone하려면 GitHub 접근 권한과 인증이 필요합니다.
- Docker Engine 또는 Docker Desktop을 설치하고 실행합니다.
- Docker Compose 2.20 이상을 준비합니다. 루트 구성은 Compose `include`를 사용합니다.
- 기본 웹 포트 `8080`을 사용할 수 있어야 합니다.
- 최초 빌드에는 컨테이너 레지스트리와 Python·npm 패키지 저장소에 접근할 인터넷 연결이 필요합니다.

앱 실행용 Python·Node.js·npm·uv를 PC에 별도로 설치할 필요는 없습니다. 다음 작업이 Docker 빌드와 시작 과정에 포함됩니다.

| 단계 | 자동 준비 내용 |
| --- | --- |
| 백엔드 이미지 빌드 | `uv sync --frozen --no-dev --no-install-project`로 잠금 파일 기준 실행 의존성 설치 |
| 프론트엔드 이미지 빌드 | `npm ci`로 잠금 파일 기준 의존성 설치 후 `npm run build` 실행 |
| 최종 이미지 | 백엔드 실행 환경과 Nginx 정적 웹 서버 구성 |
| 앱 시작 | SQLite 파일과 필요한 테이블 준비, healthcheck로 API 준비 상태 확인 |

이미지와 의존성 설치 결과는 빌드 캐시로 재사용될 수 있습니다. 소스나 잠금 파일을 바꾼 뒤에는 `--build`를 포함해 다시 실행합니다. pytest·Playwright 같은 개발용 검사 도구와 개인 Codex 스킬·MCP 설정은 앱 실행 이미지에서 자동 설치하지 않습니다.

### 환경변수와 데이터

기본 로컬 Docker 실행은 환경변수 파일 복사 없이 가능합니다. Compose가 다음 설정을 제공합니다.

| 항목 | Docker 기본값·용도 |
| --- | --- |
| `HARNESS_PORT` | `8080`: PC에서 접속할 포트 |
| `HARNESS_DATABASE_PATH` | 컨테이너 내부 `/app/data/harness.sqlite3`; Compose에서 지정 |
| `HARNESS_ALLOWED_ORIGINS` | `http://127.0.0.1:8080`, `http://localhost:8080` |
| `HARNESS_COOKIE_SECURE` | 로컬 HTTP에서는 `false`; HTTPS 운영에서는 `true`로 설정 |

세션 유효 시간은 앱 기본값 8시간입니다. `HARNESS_SESSION_HOURS`를 Docker에서 바꾸려면 Compose의 backend `environment`에도 해당 항목을 추가해야 합니다. 호스트의 모든 환경변수가 자동 전달되는 구성은 아닙니다.

사전 데이터 입력과 기본 관리자 계정은 없습니다. 처음 접속해서 회원가입합니다. 업무가 없는 계정은 샘플 업무 7개를 선택적으로 추가할 수 있습니다. SQLite 파일은 Compose의 `harness-data` 볼륨에 저장됩니다. 실제 볼륨 이름에는 Compose 프로젝트 이름이 접두사로 붙습니다.

### Docker 없이 로컬 개발·검사를 할 경우

Node.js 22.12 이상, npm, uv, Python 3.12, make가 필요합니다. Python은 uv가 선택하며, 설치된 Python이 없으면 uv가 다운로드할 수 있습니다. 환경 예시는 `boilerplates/fastapi-react/backend/.env.example`과 `frontend/.env.example`을 참고합니다. 브라우저 검사에는 Playwright Chromium 설치도 필요합니다.

## 4. 실행 방법

### Docker 실행·빌드·열람

아래 명령은 저장소 루트 기준입니다.

```sh
git clone https://github.com/elaus00/Harness.git
cd Harness
docker compose up --build -d --wait
```

이미 소스를 가지고 있다면 저장소 루트에서 마지막 명령만 실행합니다. 빌드와 설치가 끝나고 두 서비스가 준비되면 접속합니다.

| 용도 | 주소 |
| --- | --- |
| 로그인·대시보드 | [http://127.0.0.1:8080](http://127.0.0.1:8080) |
| API 문서 | [http://127.0.0.1:8080/docs](http://127.0.0.1:8080/docs) |
| API 상태 확인 | [http://127.0.0.1:8080/api/v1/health](http://127.0.0.1:8080/api/v1/health) |

```sh
# 이미지 빌드만 실행
docker compose build

# 서비스 상태와 로그 확인
docker compose ps
docker compose logs -f

# 종료: 데이터 볼륨 유지
docker compose down

# 기존 이미지로 다시 시작
docker compose up -d --wait
```

8080이 사용 중이면 포트와 허용 Origin을 함께 변경합니다. 다음은 macOS/Linux 셸 예시입니다.

```sh
HARNESS_PORT=8081 \
HARNESS_ALLOWED_ORIGINS='["http://127.0.0.1:8081","http://localhost:8081"]' \
docker compose up --build -d --wait
```

이때 접속 주소는 `http://127.0.0.1:8081`입니다. 이후 Compose 명령에도 같은 환경 설정을 유지하세요. 데이터 연속성을 위해 실행 폴더와 Compose 프로젝트 이름을 일관되게 사용합니다. `docker compose down -v`는 계정·업무 데이터가 담긴 볼륨도 삭제하므로, 데이터를 초기화하려는 경우에만 사용합니다.

### 로컬 개발 서버 실행

저장소 루트에서 시작합니다.

```sh
cd boilerplates/fastapi-react
make install
```

같은 폴더를 연 터미널 두 개에서 각각 실행합니다.

```sh
make backend
```

```sh
make frontend
```

화면은 `http://127.0.0.1:5173`, API 문서는 `http://127.0.0.1:8000/docs`입니다. Docker 실행 주소와 구분하세요.

기본 API 포트가 사용 중이라면 다음처럼 변경할 수 있습니다. 첫 명령은 backend 폴더, 두 번째 명령은 frontend 폴더에서 실행합니다.

```sh
uv run --locked uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```

```sh
API_PROXY_TARGET=http://127.0.0.1:8001 npm run dev
```

## 5. 이용 순서와 대표 결과

1. 실행 주소를 열고 **계정 만들기**를 선택합니다.
2. 이름·이메일·12자 이상 비밀번호를 입력해 가입합니다. 가입 직후 개인 대시보드로 이동합니다.
3. **만들기**에서 업무 제목·프로젝트·우선순위를 지정하거나, 빈 계정에서 **샘플 업무 불러오기**를 선택합니다.
4. 상태를 해야 할 일·진행 중·완료로 변경합니다. 검색·상태 탭·프로젝트 필터로 목록을 좁힐 수 있습니다.
5. 요약 수치, 프로젝트 완료율, 최근 활동에 실제 저장 결과가 반영되는지 확인합니다.
6. 새로고침해도 로그인 상태와 업무가 유지되는지 확인합니다. 로그아웃하면 로그인 화면으로 돌아갑니다.

대표 결과:

- 빈 계정에서 샘플 추가 시 업무 7개와 활동 기록이 나타납니다.
- 업무를 완료로 바꾸면 완료 수와 해당 프로젝트의 완료율이 갱신됩니다.
- 다른 계정으로 로그인하면 기존 계정의 업무가 보이지 않습니다.
- 기본 세션 유효 기간 안에서 컨테이너를 재시작하면 데이터와 로그인 상태가 유지됩니다.
- 상태 확인 API는 `{"status":"ok","service":"harness-api"}`를 반환합니다.

공통 문서 템플릿을 다른 프로젝트에 적용하려면 저장소 루트에서 아래 명령으로 먼저 미리봅니다.

```sh
python3 scripts/apply.py "/절대/경로/프로젝트"
python3 scripts/apply.py "/절대/경로/프로젝트" --apply
```

이 도구는 호스트 Python이 필요하며 Docker 앱 실행과 독립적입니다. 기존 파일을 덮어쓰지 않으므로 기존 문서와 필요한 규칙은 결과 안내를 보고 병합합니다.

## 6. 테스트

### Docker 실행 확인

저장소 루트에서 실행합니다. 애플리케이션용 도구를 호스트에 설치하지 않고 확인할 수 있습니다.

```sh
docker compose config --quiet
docker compose build
docker compose up -d --wait
docker compose ps
```

backend와 frontend의 상태가 `healthy`인지 확인합니다. 브라우저에서 `/api/v1/health` 응답과 회원가입·로그인·업무 생성·수정·새로고침·로그아웃 흐름을 확인합니다.

### 개발용 자동 검사

다음 검사는 호스트에 준비한 로컬 개발 환경을 사용합니다. 실행용 Docker 이미지에는 pytest·Ruff·Playwright가 포함되지 않습니다.

```sh
# 저장소 루트: 프로젝트 적용 도구
python3 -m unittest discover -s tests -v

# 앱 의존성 설치 후 정적 검사·API 검사·빌드
cd boilerplates/fastapi-react
make install
make check

# 실제 개발 서버의 HTML·API·프록시 연결
make smoke

# 브라우저 설치 및 실제 사용자 흐름 검사
cd frontend
npx playwright install chromium
cd ..
make e2e
```

| 검사 | 확인 내용 |
| --- | --- |
| 템플릿 unittest | 미리보기 무변경, 재적용 시 사용자 파일 보존, 경로 충돌 차단 |
| API pytest | 비밀번호 해시, 세션 교체·만료·폐기, 가입 검증, 요청 출처, 요청 제한, 업무 소유권, 샘플 중복 방지 |
| Ruff·Oxlint·TypeScript·Vite | 코드 검사, 타입 확인, 배포용 프론트엔드 빌드 |
| HTTP smoke | 임시 포트의 FastAPI, Vite HTML, API 프록시 연결 |
| Playwright E2E | 가입·샘플·업무 생성·수정·검색·새로고침·모바일 탐색·로그아웃·재로그인 |

2026-11-05 기준 템플릿 검사 6개, API 검사 11개, 브라우저 흐름 검사 1개와 lint·타입 검사·빌드를 통과했습니다. Docker에서는 이미지 빌드, Nginx 프록시, 인증·업무 저장, 백엔드 재시작 후 데이터·세션 유지까지 확인했습니다. 이는 당시 검증 결과이며 위 명령으로 현재 환경에서 재확인할 수 있습니다.

## 7. 가정과 제한 사항

- 기본 구성은 개인 작업용 로컬 HTTP 앱입니다. 웹 포트는 `127.0.0.1`에만 공개합니다.
- 최초 Docker 빌드에는 인터넷이 필요합니다. 베이스 이미지는 태그 기준이며, 모든 이미지가 digest로 고정된 완전한 재현 빌드는 아닙니다. 앱 의존성은 잠금 파일을 사용합니다.
- 검증한 Docker 환경은 Docker Desktop 4.38, Engine 27.5.1, Compose 2.32.4의 `linux/arm64`입니다. 다른 CPU 아키텍처·운영체제의 빌드와 실행은 추가 확인이 필요합니다.
- SQLite 단일 인스턴스 저장 방식입니다. 다중 서버 운영, DB 마이그레이션·백업, 팀 권한은 별도 설계가 필요합니다.
- 로그인·가입은 직접 연결 IP 기준 요청 제한을 적용합니다. Docker의 Nginx 뒤에서는 여러 사용자가 같은 제한을 공유할 수 있어 운영 환경의 프록시와 rate limit 구성이 필요합니다.
- 변경 API에는 허용 Origin 검사와 `X-Requested-With: Harness` 헤더가 필요합니다. API 문서나 외부 클라이언트에서 직접 요청할 때도 이 조건을 충족해야 합니다.
- HTTPS 운영에는 TLS 종료 지점, 실제 허용 Origin, Secure 쿠키 설정이 필요합니다. 기본값 그대로 인터넷에 공개하는 운영 배포는 검증 범위에 포함하지 않았습니다.
- 이메일 형식은 검증하지만 이메일 소유권은 확인하지 않습니다. 비밀번호 재설정·외부 SSO는 제공하지 않습니다.
- Atlassian 토큰 기반의 로컬 UI이며 Jira 서버와 연결된 제품은 아닙니다.
- Docker는 웹 앱의 의존성을 준비합니다. 개인 Codex 스킬 설치, MCP 인증·연결, 다른 프로젝트에 Harness 문서를 적용하는 작업까지 수행하지는 않습니다.
