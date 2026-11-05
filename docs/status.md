# 현재 상태

기준일: 2026-11-05 (Asia/Seoul)

## 목표

개인 워크플로우를 별도 Harness에서 관리하고 프로젝트별로 적용한다.

## 진행

- 사용자가 별도 Harness 폴더와 프로젝트별 적용 방식을 선택했다.
- 기존 brainstorming과 Impeccable 계열 18개 스킬을 확인했다.
- 기존 Claude 명령 `clear-with-insight`를 발견했다.
- 기본 문서·프로젝트 템플릿·회고 스킬·적용 도구를 구성했다.
- 기존 19개 스킬과 신규 회고 스킬의 설치 위치·출처·파일 해시를 `skills-lock.json`에 기록했다.
- 적용 도구의 6개 검사가 통과했다. 미리보기 무변경, 재적용 보존, 기존 스킬 전체 보존, 심링크·경로 충돌 차단, 잘못된 대상 거부를 확인했다.
- 회고 스킬 형식 검사, Harness와 적용된 템플릿의 문서 링크, 20개 스킬의 기록된 파일 해시 검증을 통과했다.
- Context7 설치와 도구 제공이 확인됐다.

## 풀스택 기반 추가 (2026-11-03)

- [FastAPI + React·Vite 보일러플레이트](../boilerplates/fastapi-react/README.md)에 의존성 설치, API 라우터, 프론트엔드 연결 화면, 잠금 파일과 실행 명령을 구성했다.
- API 테스트 3개(경고 오류 처리), lint, 타입 검사, 빌드, 실제 HTTP 프록시 검증이 통과했다.
- 임시 검증 서버는 종료했다. 실행은 해당 폴더에서 `make backend`, `make frontend`를 각각 사용한다.
- 브라우저 클릭 자동화와 운영 배포는 수행하지 않았다.

## 인증·대시보드 추가 (2026-11-05)

- 이메일·비밀번호 가입/로그인, HttpOnly 세션 유지·만료·로그아웃, SQLite 저장, 계정별 업무 분리를 구현했다.
- Atlassian 공식 토큰, 공통 UI, 로그인 화면, 대시보드, 프로젝트 요약, 검색·필터·업무 생성·상태 변경·최근 활동을 연결했다.
- `make check` 통과: API 테스트 11개, Ruff, 프론트 lint, TypeScript와 Vite 빌드.
- `make e2e` 통과: 가입·샘플·생성·수정·검색·새로고침·모바일·로그아웃·재로그인. 데스크톱/모바일 화면을 직접 확인했다.
- [설정과 실행 안내](../boilerplates/fastapi-react/README.md), [디자인 시스템](../boilerplates/fastapi-react/DESIGN_SYSTEM.md), [구축 기록](plans/2026-11-05-auth-dashboard.md).
- 현재 로컬 미리보기는 http://127.0.0.1:5173 (API 8001)에서 실행 중이다. 기존 8000 포트 프로세스는 유지했다.
- 기본 계정은 없다. 화면에서 회원가입하고 샘플 업무를 선택적으로 추가한다. 이메일 소유권 검증·비밀번호 재설정·팀 권한은 포함하지 않는다.

## README·Docker (2026-11-05)

- 루트 README에 기능·설치·개발·Docker 실행·검증 방법을 정리했다.
- API와 Nginx 이미지 빌드, Compose 실행과 건강 상태, 인증·업무 저장과 재시작 후 데이터 유지 검증을 통과했다.
- 검증 환경은 linux/arm64이다. [검증 기록](plans/2026-11-05-readme-docker.md)에 상세 내용을 남겼다.
- 이번에 생성한 테스트 컨테이너와 테스트 볼륨은 정리했다. 기본 실행은 저장소 루트 `docker compose up --build -d --wait`이다.
- 업로드 대상은 기존 비공개 `elaus00/Harness`의 main이다.

## 다음

1차 구축의 구현 작업은 완료했다. 실제 사용할 프로젝트가 정해지면 미리보기하고 필요한 규칙을 병합한다. 현재 다른 프로젝트에는 적용하지 않았다. 기존 Impeccable의 최신 단일판 전환과 추가 개발 스킬 설치는 선택 후속 항목이다.

## 회고

최신 테스트 클라이언트의 의존성 전환을 [교훈](lessons/2026-11-03_starlette-testclient.md)에 기록했다. 스킬 버전 확인의 제약과 프로젝트 적용 범위는 [도구 안내](tools.md)와 [구조 결정](decisions/0001-harness-layout.md)에 기록했다.

## 제약

앱의 기존 Harness 프로젝트 연결 경로는 상위 `/Users/elaus/Projects`이다. 실제 원본 작업 폴더는 `/Users/elaus/Projects/Harness`이다. 앱 프로젝트 경로 변경은 수행하지 않았다.
