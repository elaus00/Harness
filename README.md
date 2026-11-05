# Harness

SK하이닉스 해커톤에서 사용할 작업 규칙·문서·스킬과 선택적 앱 연결부를 모은 보관소입니다. 별도 디렉터리에 clone한 뒤 필요한 파일만 응시 작업 폴더로 꺼내 씁니다.

## 파일 꺼내 쓰기

먼저 하네스를 별도 폴더에 받습니다.

```sh
git clone https://github.com/elaus00/Harness.git
cd Harness
```

다음 명령은 **clone한 Harness 디렉터리에서** 실행합니다. `/path/to/exam-project`를 이미 존재하는 실제 작업 폴더 경로로 바꾸세요. 경로에 공백이 있으면 따옴표로 감쌉니다.

```sh
# 문서·스킬·최소 앱 연결부: 먼저 미리보기
python3 scripts/apply.py /path/to/exam-project --profile exam

# 확인한 파일을 실제로 적용
python3 scripts/apply.py /path/to/exam-project --profile exam --apply

# 문서와 스킬만 적용
python3 scripts/apply.py /path/to/exam-project --profile docs --apply

# Polars·humanizer-ko를 포함한 스킬 9개만 일괄 설치
python3 scripts/apply.py /path/to/exam-project --skills-only --apply
```

필요한 구성에 맞는 명령을 선택합니다. 적용 도구는 Python 3.8 이상 표준 라이브러리만 사용합니다. `--apply`가 없으면 파일을 쓰지 않습니다.

응시 환경의 README·AI_COLLABORATION 양식은 보존합니다. exam·docs 프로필은 기존 파일의 내용·경로가 충돌하면 적용 전에 중단하고, 기존 스킬은 폴더 전체를 유지합니다. 앱 실행과 환경 설정은 [기반 사용법](templates/exam/docs/OPERATIONS.md)을 참고하세요.

Docker 구성·컴파일은 실제 과제 요구에 맞춰 사용자가 지정 디렉터리에서 별도로 수행합니다. Docker 파일은 시험용 추출 대상에 포함되지 않습니다.

## 문서

- [3시간 AI 과제 진행 절차](workflow.md)
- [선택 적용·포함 내용 안내](START_HERE.md)
- [시험용 앱 실행·설정·검사](templates/exam/docs/OPERATIONS.md)
- [스킬 목록·설치 안내](docs/tools.md)
- [작업 문서 색인](docs/index.md)
- [기존 대시보드 예제 실행 안내](How_to_run.md)
