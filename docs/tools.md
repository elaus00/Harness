# 스킬과 연결 도구

확인일: 2026-11-02. [설치 상태 기록](../skills-lock.json)은 로컬 파일 해시와 출처를 기록한다. 인증 정보는 포함하지 않는다.

## 현재 사용

| 구성 | 상태·위치 | 적용 조건 |
| --- | --- | --- |
| brainstorming | 기존 `~/.agents/skills/brainstorming` | 새 기능과 큰 구조 변경의 설계 |
| Impeccable | 기존 `~/.agents/skills/`의 개별 스킬 18개 | UI 생성·검토·개선 시 필요한 스킬 선택 |
| clear-with-lessons | 이 프로젝트의 `.agents/skills/clear-with-lessons` | 의미 있는 작업 완료·종료·인계 |
| GitHub | 기존 플러그인 설치 확인 | 저장소·PR·이슈 작업 |
| Context7 | 이번 세션에서 설치 및 도구 제공 확인 | 라이브러리 문서·예제 확인 |

brainstorming과 Impeccable은 이미 설치되어 있어 다시 다운로드하지 않았다. 회고 스킬은 Claude의 `~/.claude/commands/clear-with-insight.md`를 기반으로 새로 작성했다. 원본은 보존했다. 프로젝트 적용 도구는 이 새 스킬을 대상 프로젝트에 복사하며 전역 외부 스킬까지 복사하지 않는다.

## 다른 환경에 설치

이 컴퓨터의 기존 설치본은 원본 커밋/릴리스가 기록되어 있지 않다. `skills-lock.json`의 `upstream_commit: null`은 이를 뜻하며 로컬 해시를 Git 커밋처럼 사용할 수 없다. 아래 공식 출처에서 원하는 버전을 선택하고, 설치 전에 경로와 의존 관계를 확인한다. 파일 몇 개만 복사하면 스킬의 참조 문서나 실행 파일이 누락될 수 있다.

- [Superpowers 공식 배포](https://github.com/obra/superpowers): brainstorming 및 관련 개발 스킬. 새 환경에서는 `skill-installer`로 선택한 저장소 경로와 커밋을 지정해 설치할 수 있다.
- [Impeccable 공식 설치 안내](https://github.com/pbakaus/impeccable#installation): 현재 배포는 단일 impeccable 스킬 구조다. 기존 18개 구성에서 전환할 때 백업과 중복 활성화 여부를 먼저 검토한다. 이번 구축에서는 전환하지 않았다.
- [Codex 스킬 안내](https://learn.chatgpt.com/docs/build-skills): 프로젝트 `.agents/skills/`의 스킬은 해당 프로젝트를 작업 폴더로 열어 사용한다. 새 스킬이 보이지 않으면 해당 폴더에서 새 세션을 시작한다.

## 추가 후보

| 후보 | 도입 이유 | 현재 결정 |
| --- | --- | --- |
| writing-plans | 큰 작업을 결과물과 검증 단위로 분해 | 원칙만 참고, 별도 설치 안 함 |
| systematic-debugging | 재현·원인·수정의 순서로 버그 조사 | 실제 버그 작업이 늘 때 검토 |
| verification-before-completion | 완료 주장 전에 증거 확보 | 기본 문서에 원칙 반영, 별도 설치 안 함 |
| OpenAI Docs MCP | Codex와 OpenAI API 공식 문서 조회 | 필요 시 선택 추가 |

Superpowers는 스킬 사이의 의존 관계가 있다. 일부 이름만 설치한 뒤 전체 워크플로우가 준비됐다고 간주하지 않는다. writing-plans는 executing-plans 또는 subagent-driven-development를 참조하고, 실행 과정의 종속 스킬도 확인해야 한다.

- [검토한 writing-plans 원문](https://github.com/obra/superpowers/blob/2ce8aa15d05bd57213e6f746f953aafb7ded7a8b/skills/writing-plans/SKILL.md)
- [OpenAI Docs MCP](https://developers.openai.com/learn/docs-mcp)

## 업데이트

업데이트는 현재본의 백업 → 원본 차이와 의존 관계 확인 → 선택한 버전 설치 → 스킬 인식·참조 파일 확인 → 설치 상태 기록 갱신 순으로 수행한다. 사용자 설정과 비밀값은 템플릿에 포함하지 않는다. 이 기록은 새로운 환경의 인증 상태나 도구 연결까지 복원하지 않는다.
