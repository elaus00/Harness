# 현재 상태

기준일: 2026-11-05 (Asia/Seoul)

## 목표

SK하이닉스 해커톤의 웹 IDE 가상 컴퓨터에 저장소를 별도 보관용으로 clone하고, 문제와 무관한 파일을 응시 작업 디렉터리로 꺼내 쓸 수 있게 한다. 원문 보존·선택 적용·문서·스킬·재사용할 앱 연결부가 범위다. Docker 구성·컴파일은 사용자가 실제 지정 디렉터리에서 수행하며 하네스 완료 조건에서 제외한다. 현재 진입점은 [START_HERE](../START_HERE.md)다.

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

## 실행 안내 추가 (2026-11-05)

- [How_to_run.md](../How_to_run.md)를 요청한 7개 항목으로 작성했다.
- Docker 빌드의 uv/npm 의존성 설치, 시작 시 DB 준비, 호스트 개발 도구가 필요한 검사 범위를 구분했다.
- 설정·명령을 현재 Dockerfile·Compose·Makefile과 대조했다. 문서 변경이므로 이미 통과한 앱 검사를 다시 실행하지 않았다.

## 다음

파일 추출형 보완의 구현·로컬 검증을 완료했다. [검증 기록](plans/2026-11-05-portable-exam.md)과 [구조 결정](decisions/0002-exam-extraction.md)을 참고한다. 최초 요구사항·보완 전 점검은 과거 기록으로 보존했다.

- `templates/exam/`의 40개 파일을 `exam-files.json`으로 관리한다. 원문 README·AI_COLLABORATION·Docker 파일·실제 .env·가상환경·DB는 추출하지 않는다. 기존 대시보드는 별도 예제로 유지한다.
- `scripts/apply.py`의 `--profile docs`, `--profile exam`, `--skills-only`로 선택 적용한다. exam·docs는 기존 내용·대소문자·심링크 충돌을 적용 전에 검사하며 기존 스킬은 폴더 전체를 보존한다.
- 루트 README에도 미리보기·전체 틀·문서·스킬 일괄 설치 명령, 실행 위치·대상 경로·보존 동작을 명시했다. 기존 Docker 중심 소개를 현재 파일 추출 방식에 맞췄다. 문서 링크와 CLI 옵션을 대조했으며 문서 변경만으로 앱 테스트를 재실행하지 않았다.
- 시험용 AGENTS·INDEX·F/D/A DECISION·PRD·STATUS·TASKS·빈 HOW_TO_RUN과 붙여넣기 프롬프트를 제공한다. 응시 목적·도메인 규칙·가중치는 비워 뒀다.
- Polars·humanizer-ko·회고와 반복 작업 6개를 합한 9개 스킬을 동봉한다. `skills-bundle.lock.json`은 현재 동봉본, 기존 `skills-lock.json`은 개인 전역 설치 목록이다. 해시 갱신은 `python3 scripts/update_bundles.py --date YYYY-MM-DD`로 수행한다.
- 선택적 앱은 FastAPI·정적 프론트, SQLite WAL·DB 준비 상태, 환경변수 오류·두 역할 인증·서버 권한, CSV 구문 검사·버전 원자적 적용, 생성 잠금·실패 복구·버전 추적·stale Export 차단을 제공한다. engine·validator는 빈 인터페이스이며 미구현은 501이다.
- 적용 도구 14개와 앱 28개 테스트, Ruff·JS·스킬 형식·정적 의존성 검사를 통과했다. 별도 추출본의 자체 의존성 설치·실제 HTTP·Chromium 로그인·CSV 적용·501·로그아웃·읽기 권한 403과 모바일 화면도 확인했다. 임시 서버·작업 폴더는 정리했다.
- 이번 로컬 보완의 남은 구현 작업은 없다. 실제 시험 규정·Git 접근·AI 호스트 스킬 인식·웹 IDE·3시간 리허설은 현장 확인 사항이다. Docker는 이번 범위에서 제외했다.
- 사용자 제공 3시간 과제 절차를 루트 `workflow.md`에 본문 변경 없이 저장하고 README·색인에서 연결했다. 문서의 Docker·현장 도메인 예시는 사용자 원문이며 하네스 추출본의 사전 구현 범위를 확대하지 않는다. 사용자 요청에 따라 이 문서와 지금까지의 전체 변경을 Git 커밋·푸시 대상으로 정리했다. 실제 원격 반영은 Git 이력으로 확인한다.
- 첫 50분 절차를 `FIRST_50_MIN_CHECKLIST.md`에 체크박스로 정리하고 README·색인에서 연결했다. NOTES 복귀 준비, 직접 읽기·AI 병렬 작업, 묶음 질문, 50분 기준 확정, 2시간 30분 기능 중단을 포함한다. 문서 링크·형식을 확인했으며 코드 변경이 없어 앱 검사는 재실행하지 않았다.

## 회고

최신 테스트 클라이언트의 의존성 전환을 [교훈](lessons/2026-11-03_starlette-testclient.md)에 기록했다. 스킬 버전 확인의 제약과 프로젝트 적용 범위는 [도구 안내](tools.md)와 [구조 결정](decisions/0001-harness-layout.md)에 기록했다.

이번 파일 추출형 보완에서는 별도로 저장할 교훈은 없다. 실제 변경·검증·남은 현장 확인은 위 상태와 검증 기록에 남겼다.

## 제약

앱의 기존 Harness 프로젝트 연결 경로는 상위 `/Users/elaus/Projects`이다. 실제 원본 작업 폴더는 `/Users/elaus/Projects/Harness`이다. 앱 프로젝트 경로 변경은 수행하지 않았다.
