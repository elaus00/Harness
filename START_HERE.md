# 시험용 Harness 파일 꺼내 쓰기

이 저장소는 **별도 디렉터리에 clone해 두는 보관소**다. 응시 루트에 전체를 복사하지 않고 `templates/exam/`에서 필요한 파일만 가져온다. 원본 README와 AI_COLLABORATION 양식은 대상 환경에 그대로 둔다.

보관소에는 기존 앱 예제·README·Docker 구성이 남아 있다. 시험용 추출본에는 이 파일들이 포함되지 않는다. Docker 구성·빌드는 사용자가 실제 과제 요구에 맞춰 지정 디렉터리에서 나중에 수행하며 하네스 준비 조건에서 제외한다.

## 선택 적용

아래는 **clone한 Harness 디렉터리에서** 실행한다. 대상 폴더는 먼저 만들어 둔다. 기본은 미리보기이며 `--apply`로 신규 파일만 생성한다.

```sh
# 문서·스킬과 최소 앱 연결부
python3 scripts/apply.py /path/to/exam-project --profile exam
python3 scripts/apply.py /path/to/exam-project --profile exam --apply

# 문서와 스킬만 필요할 때
python3 scripts/apply.py /path/to/exam-project --profile docs --apply

# 동봉 스킬 9개만 한 번에 설치
python3 scripts/apply.py /path/to/exam-project --skills-only --apply
```

Python 3.8 이상 표준 라이브러리만 사용한다. 원본 파일 해시를 확인하고 문서·경로·대소문자·심링크 충돌은 쓰기 전에 알린다. exam·docs 프로필에서 기존 파일 내용이 다르면 전체 적용을 중단한다. 기존 스킬은 해당 폴더 전체를 보존한다. 기존 AGENTS가 있다면 빈 준비 폴더로 추출한 뒤 검토·병합한다. 앱이나 문서를 자동 업데이트하는 명령은 아니다.

수동으로 파일을 골라 가져와도 된다. 앱을 가져오면 `contracts.py`, `engine/`, `validator/`, `app/`, `pyproject.toml`, `uv.lock`, `.env.example`이 연결된 단위다. 문서·스킬은 독립적으로 선택할 수 있다.

## 포함 내용

- 짧은 시험용 AGENTS, 목적을 비워 둔 PRD, F/D/A 결정 기록, INDEX·STATUS·TASKS, 빈 HOW_TO_RUN.
- 요구사항 정리·데이터 프로파일·독립 검증기·데이터 변형·복귀·문서 마무리 스킬 6개와 Polars·humanizer-ko·회고 스킬.
- SQLite WAL·스키마·DB 상태 확인, 선택적 두 역할 인증, 환경변수 설정·공통 오류 형식을 가진 최소 FastAPI·정적 화면.
- 선택적 데이터셋 구문 확인·원자적 버전 적용·생성 잠금·결과 버전 추적·재계산 표시·화면/복사/서버 저장 Export.
- 빈 engine·독립 validator 인터페이스, 동작·권한·원자성·의존성 테스트, clone 불가 대비 [붙여넣기용 프롬프트](templates/exam/prompts/QUICKSTART.txt).

기본 앱에서는 인증·생성형 과제 기능이 꺼져 있다. 도메인 알고리즘·검증 규칙·가중치·역할명·Export 열은 현장 README를 읽고 결정한다. CSV 구문 확인은 도메인 검증이 아니다. 빈 생성기·검증기는 501로 실패하며 성공 결과를 가장하지 않는다.

앱 실행·환경 설정·API·작업 복구는 [기반 사용법](templates/exam/docs/OPERATIONS.md)을 참고한다. [구현·검증 계획](docs/plans/2026-11-05-portable-exam.md)에 실제 검증 결과를 기록한다. 주최 측 반입 규정과 실제 IDE·리허설 결과는 별도로 확인한다.
