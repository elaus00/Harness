# README와 Docker 검증

날짜: 2026-11-05. 사용자 요청: README 작성, GitHub 업로드, Docker 빌드 확인.

## 변경

- 루트 README에 기능, Docker/로컬 실행, 테스트, 구조, 설정, 인증 범위를 정리했다.
- 백엔드는 uv 잠금 파일 기준으로 개발 의존성을 제외한 Python 3.12 이미지와 비루트 실행을 구성했다.
- 프론트엔드는 Node 24에서 정적 파일을 빌드하고 Nginx 1.28에서 서비스한다. `/api`는 backend로 전달한다.
- 독립 앱 Compose와 루트 include 진입점, healthcheck, SQLite named volume을 구성했다.
- Docker build context에서 `.env`, DB, 로컬 설치 결과와 테스트 산출물을 제외했다.

## 검증 결과

- Docker Compose config와 backend/frontend 이미지 빌드 성공.
- Docker Desktop 4.38 / Engine 27.5.1 / Compose 2.32.4, linux/arm64에서 확인했다. 다른 아키텍처 빌드는 별도 확인하지 않았다.
- 격리된 `harness-verify` 프로젝트, 18080 포트에서 실제 실행했다.
- 정적 HTML, OpenAPI, Nginx API 프록시, 회원가입·세션·업무 저장·로그아웃·재로그인 통과.
- 백엔드 재시작 후 SQLite 데이터와 세션이 유지되는 것을 확인했다.
- 템플릿 검사 6개, API 검사 11개, lint·타입 검사·Vite 빌드 통과.
- 검증용 컨테이너와 해당 테스트 볼륨만 정리했다. 기존 로컬 개발 서비스와 데이터는 보존했다.

원격 대상은 기존 비공개 저장소 `elaus00/Harness`, 기본 브랜치 `main`이다. 공개 범위는 변경하지 않는다.
