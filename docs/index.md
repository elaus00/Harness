# 문서 색인

먼저 현재 상태를 확인한 뒤 작업과 관련된 문서만 읽는다.

| 문서 | 목적 | 상태 |
| --- | --- | --- |
| [작업 규칙](../AGENTS.md) | 상시 작업 원칙 | 사용 |
| [실행 안내](../How_to_run.md) | 준비·실행·이용·테스트·제한 사항 | 사용 |
| [현재 상태](status.md) | 완료 사항·다음 작업·제약 | 사용 |
| [작업 흐름](workflow.md) | 시작부터 검증·회고까지 | 사용 |
| [스킬과 도구](tools.md) | 설치 상태·선택 기준·업데이트 | 사용 |
| [구조 결정](decisions/0001-harness-layout.md) | 별도 폴더와 프로젝트별 적용을 선택한 이유 | 채택 |
| [초기 구축 계획](plans/2026-11-02-bootstrap.md) | 1차 범위와 완료 기준 | 완료 |
| [프로젝트 템플릿](../templates/project/AGENTS.md) | 새 프로젝트 적용의 시작점 | 사용 |
| [회고 스킬](../.agents/skills/clear-with-lessons/SKILL.md) | 교훈 저장과 다음 세션 인계 | 사용 |
| [FastAPI + React·Vite](../boilerplates/fastapi-react/README.md) | 실행 가능한 풀스택 보일러플레이트 | 사용 |
| [보일러플레이트 구축](plans/2026-11-03-fastapi-react.md) | 구성과 검증 결과 | 완료 |
| [Starlette 테스트 클라이언트 교훈](lessons/2026-11-03_starlette-testclient.md) | 최신 테스트 의존성 전환과 검증 | 사용 |
| [인증·대시보드](plans/2026-11-05-auth-dashboard.md) | 구성과 검증 결과 | 완료 |
| [디자인 시스템](../boilerplates/fastapi-react/DESIGN_SYSTEM.md) | Atlassian 토큰과 공통 UI | 사용 |
| [SQLite 요청 수명 교훈](lessons/2026-11-05_fastapi-sqlite-thread.md) | 실제 브라우저에서 발견한 연결 문제 | 사용 |
| [README·Docker 검증](plans/2026-11-05-readme-docker.md) | 컨테이너 빌드·인증·데이터 유지 검증 | 완료 |

## 관리 규칙

문서 생성·이동·폐기 시 이 표를 함께 갱신한다. 문서 본문을 색인에 복제하지 않는다. 교훈은 실제로 발견한 때 `lessons/YYYY-MM-DD-주제.md`에 추가하고 여기에서 연결한다. 사용자 조치가 생겼을 때만 `request.md`를 생성하고 연결한다. 폐기 문서는 상태와 대체 링크를 남긴다.
