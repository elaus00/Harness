# 개인 Harness

공통 작업 방식과 템플릿을 관리하고 필요한 프로젝트에 선택적으로 적용한다.

- [문서 진입점](docs/index.md)
- [현재 상태](docs/status.md)
- [작업 흐름](docs/workflow.md)
- [스킬과 연결 도구](docs/tools.md)

## 프로젝트에 적용

Python 3만 필요하다. 대상 프로젝트 폴더는 먼저 존재해야 한다.

```sh
python3 scripts/apply.py "/절대/경로/프로젝트"
python3 scripts/apply.py "/절대/경로/프로젝트" --apply
```

첫 명령은 미리보기이며 두 번째 명령이 신규 파일을 추가한다. 기존 파일은 덮어쓰지 않는다. 기존 `AGENTS.md` 또는 문서가 있다면 출력된 안내를 확인하고 필요한 규칙을 직접 병합한다. 새 회고 스킬은 프로젝트의 `.agents/skills/clear-with-lessons/`로 복사한다. 전역 스킬이나 MCP 설정은 변경하지 않는다.

이 폴더를 Codex의 작업 폴더로 열면 Harness의 규칙과 회고 스킬을 사용할 수 있다. 현재 앱 프로젝트가 상위 `Projects`를 가리킨다면 별도로 이 폴더를 열어야 한다. 상위 폴더에 있다는 이유만으로 각 Git 저장소에 규칙이 적용되지는 않는다.

## 운영

템플릿과 적용된 프로젝트는 독립적인 복사본이다. 개선 사항은 여기에서 검토한 뒤 필요한 프로젝트에 선택적으로 반영한다. 기존 사용 중인 brainstorming과 Impeccable은 유지한다. 설치 현황은 `skills-lock.json`에 기록하며 이 파일은 다운로드 가능한 원본 버전을 고정하는 패키지 잠금 파일이 아닌 로컬 상태 기록이다.

## 풀스택 보일러플레이트

[FastAPI + React·Vite 시작 안내](boilerplates/fastapi-react/README.md). API와 프론트엔드를 실행하고 검증할 수 있는 독립 기본형이다.
