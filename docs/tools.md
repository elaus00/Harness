# 스킬과 연결 도구

확인일: 2026-11-05. [기존 설치 상태 기록](../skills-lock.json)은 개인 컴퓨터의 설치 목록이며, [동봉 스킬 기록](../skills-bundle.lock.json)은 clone 배포본의 상대 경로·출처·원본 커밋·파일 해시를 기록한다. 두 기록에 인증 정보는 포함하지 않는다.

## clone에 포함된 스킬과 일괄 설치

| 스킬 | 용도 | 배포본 |
| --- | --- | --- |
| [polars](../.agents/skills/polars/SKILL.md) | CSV 등 표 형식 데이터 분석·파싱·검증 | [공식 원본](https://github.com/polars-inc/skills/tree/b102cc948ba9a058f075e9794861ae5c56f31f6d/skills/polars), 본문·참조 6개·MIT 라이선스 |
| [humanizer-ko](../.agents/skills/humanizer-ko/SKILL.md) | 사실을 보존하는 자연스러운 한국어 산문 교정 | [공식 원본](https://github.com/IsaacEryn/humanizer-ko/tree/b1562c26315b8d264d7830cd98d280e4d92333ea), v1.5.0 본문·참조 2개·표시 메타데이터·MIT 라이선스 |
| [clear-with-lessons](../.agents/skills/clear-with-lessons/SKILL.md) | 세션 인계와 교훈 기록 | Harness 자체 스킬 |
| [exam-requirements](../.agents/skills/exam-requirements/SKILL.md) | 현장 요구사항 ID·수용 기준 정리 | Harness 자체 스킬 |
| [exam-data-profile](../.agents/skills/exam-data-profile/SKILL.md) | 파일별 행 의미·키·교차 점검·질문 | Harness 자체 스킬 |
| [exam-validator](../.agents/skills/exam-validator/SKILL.md) | 독립 검증기·실패 예시 작성 | Harness 자체 스킬 |
| [exam-dataset-variants](../.agents/skills/exam-dataset-variants/SKILL.md) | 원본을 보존한 정상 변경·오류 데이터 | Harness 자체 스킬 |
| [exam-resume](../.agents/skills/exam-resume/SKILL.md) | 연결 중단 후 작업 복귀 | Harness 자체 스킬 |
| [exam-finalize](../.agents/skills/exam-finalize/SKILL.md) | 실제 기록으로 제출 문서 초안 작성 | Harness 자체 스킬 |

clone 보관소에는 파일이 `.agents/skills/`에 준비되어 있다. 다른 응시 프로젝트에 9개 스킬을 한 번에 설치하려면 **Harness 루트에서** 아래 명령을 실행한다. 대상 폴더는 먼저 존재해야 한다.

```sh
python3 scripts/apply.py /path/to/exam-project --skills-only --apply
```

Python 3.8 이상 표준 라이브러리만 사용하며 네트워크·npm·uv가 필요 없다. `--apply`를 빼면 변경 없는 미리보기다. 스킬 폴더가 이미 있으면 그 스킬 전체를 보존하고 `SKIP`으로 표시한다. 자동 업데이트나 덮어쓰기는 하지 않으므로 SKIP된 스킬은 동봉본과 다를 수 있다. 심링크·경로 충돌이 있으면 쓰기 전에 중단한다.

이 명령은 `.agents/skills/`만 추가한다. 응시 환경의 `README.md`, `AI_COLLABORATION.md`, `AGENTS.md`, 앱 코드는 수정하지 않는다. 대상의 기존 AI 지침에 필요한 스킬 사용 규칙은 직접 병합해야 한다. 호스트 AI가 프로젝트 스킬을 읽는지는 해당 호스트에서 확인한다. 이 명령은 AI 확장·로그인·MCP나 Python의 `polars` 패키지를 설치하지 않는다. 선택적 exam 앱에는 Polars 실행 의존성과 uv.lock을 포함한다. Docker 구성·빌드는 사용자가 실제 지정 디렉터리에서 결정한다.

두 외부 스킬의 필요한 런타임 파일만 포함했으며 README와 저장소 관리용 파일은 복사하지 않았다. 외부 스킬 본문·참조는 고정 커밋 원본과 동일하다. 문서·앱을 함께 꺼내는 명령은 [현재 사용 안내](../START_HERE.md), 이번 보완 범위는 [파일 추출형 계획](plans/2026-11-05-portable-exam.md)을 참고한다. [해커톤 기준 점검](plans/2026-11-05-hackathon-audit.md)은 보완 전 점검 기록이다.

## 기존 개인 환경의 추가 도구

| 구성 | 상태·위치 | 적용 조건 |
| --- | --- | --- |
| brainstorming | 기존 `~/.agents/skills/brainstorming` | 새 기능과 큰 구조 변경의 설계 |
| Impeccable | 기존 `~/.agents/skills/`의 개별 스킬 18개 | UI 생성·검토·개선 시 필요한 스킬 선택 |
| clear-with-lessons | 이 프로젝트의 `.agents/skills/clear-with-lessons` | 의미 있는 작업 완료·종료·인계 |
| GitHub | 기존 플러그인 설치 확인 | 저장소·PR·이슈 작업 |
| Context7 | 이번 세션에서 설치 및 도구 제공 확인 | 라이브러리 문서·예제 확인 |

brainstorming과 Impeccable은 개인 환경에 설치되어 있으며 clone 배포본에는 포함하지 않았다. 회고 스킬은 Claude의 `~/.claude/commands/clear-with-insight.md`를 기반으로 새로 작성했다. 프로젝트 적용 도구는 동봉된 위 9개 스킬을 복사하며 전역 외부 스킬이나 MCP 설정까지 복원하지 않는다. 시험용 AGENTS는 외부 brainstorming·Impeccable 설치를 요구하지 않는다.

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
