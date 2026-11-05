# 문서 색인

먼저 현재 상태를 확인한 뒤 작업과 관련된 문서만 읽는다.

| 문서 | 목적 | 상태 |
| --- | --- | --- |
| [작업 규칙](../AGENTS.md) | 상시 작업 원칙 | 사용 |
| [하네스 README](../README.md) | clone 보관소 소개·파일 추출·스킬 일괄 설치 명령 | 사용 |
| [3시간 과제 절차](../workflow.md) | 사용자가 제공한 시작·기준 확정·검증·통합·제출 시간표 | 참고 |
| [첫 50분 체크리스트](../FIRST_50_MIN_CHECKLIST.md) | 환경 확인·지시문·질문·판단 기준 확정과 이후 시간 규칙 | 참고 |
| [파일 꺼내 쓰기](../START_HERE.md) | 현재 시험용 진입점·선택 적용 명령 | 사용 |
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
| [해커톤 요구사항·설계안](plans/2026-11-05-hackathon-requirements.md) | 최초 clone·Docker 요구 기록. 파일 추출형 계획으로 대체 | 과거 기록 |
| [해커톤 기준 점검](plans/2026-11-05-hackathon-audit.md) | 보완 전 3층 기준의 충족 여부·구조 판단 | 과거 점검 |
| [파일 추출형 계획](plans/2026-11-05-portable-exam.md) | 현재 보완 범위·구현·검증 결과 | 완료 |
| [추출 방식 결정](decisions/0002-exam-extraction.md) | clone 보관소·시험 추출본·Docker 범위 분리 | 채택 |
| [시험용 문서 색인](../templates/exam/docs/INDEX.md) | 추출본 규칙·F/D/A·PRD·진행·사용법·프롬프트 | 사용 |
| [요구사항 스킬](../.agents/skills/exam-requirements/SKILL.md) | 현장 README를 ID·수용 기준으로 정리 | 동봉 |
| [데이터 프로파일 스킬](../.agents/skills/exam-data-profile/SKILL.md) | 파일별·교차 검사·질문·가정 후보 | 동봉 |
| [독립 검증기 스킬](../.agents/skills/exam-validator/SKILL.md) | engine에 의존하지 않는 검증·실패 예시 | 동봉 |
| [데이터 변형 스킬](../.agents/skills/exam-dataset-variants/SKILL.md) | 정상 변경본·오류본·변경 근거 | 동봉 |
| [복귀 스킬](../.agents/skills/exam-resume/SKILL.md) | 중단 지점과 실제 검증을 확인해 복귀 | 동봉 |
| [제출 마무리 스킬](../.agents/skills/exam-finalize/SKILL.md) | 실제 기록으로 제출 문서 초안 준비 | 동봉 |
| [Polars 스킬](../.agents/skills/polars/SKILL.md) | CSV 등 표 형식 데이터 분석과 참조 문서 안내 | 동봉 |
| [humanizer-ko 스킬](../.agents/skills/humanizer-ko/SKILL.md) | 사실을 보존하는 한국어 산문 교정 | 동봉 |

## 관리 규칙

문서 생성·이동·폐기 시 이 표를 함께 갱신한다. 문서 본문을 색인에 복제하지 않는다. 교훈은 실제로 발견한 때 `lessons/YYYY-MM-DD-주제.md`에 추가하고 여기에서 연결한다. 사용자 조치가 생겼을 때만 `request.md`를 생성하고 연결한다. 폐기 문서는 상태와 대체 링크를 남긴다.
