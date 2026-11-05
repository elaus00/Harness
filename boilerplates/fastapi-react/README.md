# FastAPI + React · Vite

재사용할 최소 풀스택 기반. 공식 `create-vite@9.3.3`의 `react-ts` 템플릿으로 프론트엔드를 생성하고 FastAPI 앱을 구성했다. FastAPI 공식 풀스택 저장소를 검토했으며, 해당 저장소 전체를 복제한 구성은 아니다.

## 준비

- Node.js 22.12 이상 (현재 검증 환경: 25.3.0), npm, uv, make.
- 백엔드 Python 3.12는 uv가 선택한다. 시스템 `python3`가 3.8이어도 백엔드를 직접 실행하지 않고 uv를 사용한다.
- `backend/uv.lock`과 `frontend/package-lock.json`을 함께 보존한다.

## 실행

이 폴더에서 `make install`로 잠금 파일 기준 의존성을 설치한다. 현재 컴퓨터에는 설치 완료되어 있다.

두 터미널에서 각각 실행한다.

```sh
make backend
```

```sh
make frontend
```

- 화면: http://127.0.0.1:5173
- API 문서: http://127.0.0.1:8000/docs
- 상태 확인: http://127.0.0.1:8000/api/v1/health

처음에는 계정을 만든다. 회원가입 직후 대시보드로 이동하며, 업무를 직접 만들거나 ‘샘플 업무 불러오기’로 예시 7개를 추가할 수 있다. 기본 계정은 생성하지 않는다. 포트가 사용 중이면 기존 프로세스를 임의 종료하지 말고 포트를 변경한다. 백엔드 포트를 바꾸면 프론트엔드의 `API_PROXY_TARGET`도 맞춘다. `frontend/.env.example`을 `.env`로 복사해 설정할 수 있다.

## 구조

- `backend/app/main.py`: 앱 생성과 라우터 등록
- `backend/app/api/`: API 라우터와 응답 모델
- `backend/tests/`: API 계약 테스트
- `frontend/src/`: React + TypeScript 화면
- `frontend/vite.config.ts`: 개발 서버와 `/api` 프록시
- `scripts/smoke.py`: 임시 포트에서 두 서버를 시작하고 HTTP 연결 검증 후 종료

## 검증

```sh
make check
make smoke
make e2e
```

`check`는 Ruff, pytest, 프론트엔드 lint, TypeScript 검사와 Vite 빌드를 실행한다. `smoke`는 실제 HTTP 요청으로 API·Vite 페이지·Vite→API 프록시 연결을 검사한다. `e2e`는 격리된 임시 DB로 가입·업무 생성·수정·검색·새로고침·모바일·로그아웃·로그인을 검증한다. 처음 실행할 때 `cd frontend && npx playwright install chromium`이 필요할 수 있다.

## 새 프로젝트로 복사

새 빈 대상 폴더를 만들고 이 폴더에서 실행한다. 설치 결과물과 로컬 설정을 제외한다.

```sh
rsync -a --ignore-existing --exclude=node_modules --exclude=.venv --exclude=dist \
  --exclude=__pycache__ --exclude=.pytest_cache --exclude=.ruff_cache \
  --exclude=data --exclude=artifacts --exclude=test-results --exclude=playwright-report \
  --filter='+ .env.example' --filter='- .env*' \
  ./ /절대/경로/새프로젝트/
```

복사한 폴더에서 `make install`을 다시 실행한다. Harness의 공통 문서는 별도로 `scripts/apply.py`로 적용하며 기존 AGENTS.md에 공통 문서·회고 규칙을 병합한다. 이 starter의 AGENTS.md와 프로젝트 기술 규칙은 보존한다.

## 배포 전제

개발 환경에서는 브라우저가 Vite와 같은 출처의 `/api/v1/health`를 요청하고 Vite가 백엔드로 전달한다. 별도 CORS 허용은 필요하지 않다. Vite 프록시는 개발 전용이다. 운영에서는 `frontend/dist`를 정적 호스팅하고 `/api`를 FastAPI로 전달하는 같은 출처의 reverse proxy를 구성해야 한다. `npm run preview`만으로 API 연결이 제공되지는 않는다.

## 인증과 저장

SQLite에 계정·세션·업무·활동을 저장한다. 위치는 기본 `backend/data/harness.sqlite3`이며 서버를 재시작해도 보존된다. DB 파일과 data 폴더는 새 프로젝트 복사나 버전 관리에서 제외한다.

- 이메일·비밀번호 회원가입, 로그인, 현재 사용자, 로그아웃 API.
- Argon2 비밀번호 해시, 무작위 세션 토큰의 SHA-256 해시 저장, 8시간 만료.
- HttpOnly·SameSite=Lax 쿠키. 로그인 시 세션 교체, 로그아웃 시 서버에서 폐기.
- 변경 요청은 `X-Requested-With: Harness`와 허용 Origin 검증. CORS를 임의로 넓히지 않는다.
- 가입·로그인 요청은 직접 연결 IP 기준 10분당 30회. reverse proxy를 배포하면 신뢰할 프록시 설정과 운영 rate limit을 함께 구성한다.
- 업무와 활동은 로그인한 사용자별로 분리한다.

설정은 `backend/.env.example`에서 확인한다. 운영 HTTPS에서는 `HARNESS_COOKIE_SECURE=true`와 실제 `HARNESS_ALLOWED_ORIGINS`를 설정한다. 인증 브라우저 요청은 동일 출처 `/api` 프록시를 사용한다.

이 기본형에는 이메일 소유권 확인, 비밀번호 재설정, 소셜 로그인, 팀 권한과 운영용 DB 마이그레이션이 포함되어 있지 않다.

## 디자인 시스템

[디자인 시스템 안내](DESIGN_SYSTEM.md). Atlassian의 실제 `@atlaskit/tokens`와 공통 React 컴포넌트로 Jira 스타일의 개인 대시보드를 구성했다. Jira 제품과의 API 연동은 포함하지 않는다.

## 출처

- [Vite 시작 안내](https://vite.dev/guide/)
- [FastAPI 공식 풀스택 템플릿](https://github.com/fastapi/full-stack-fastapi-template)
- [FastAPI 테스트 안내](https://fastapi.tiangolo.com/tutorial/testing/)

## Docker

이 폴더 또는 저장소 루트에서 `docker compose up --build -d --wait`로 실행한다. 화면과 API는 http://127.0.0.1:8080 으로 제공하며 SQLite는 named volume에 보존한다. 빌드만 확인하려면 `docker compose build`, 종료는 `docker compose down`이다. 자세한 설정은 [저장소 README](../../README.md#docker로-빠르게-시작)를 따른다.
