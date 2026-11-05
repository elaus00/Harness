# FastAPI 요청 수명과 SQLite 연결

적용 범위: 이번 FastAPI 0.162.0, 동기 dependency와 SQLite 구성.

## 실패와 원인

API TestClient에서는 통과했지만 실제 브라우저 흐름에서 SQLite ProgrammingError가 발생했다. yield dependency 진입과 종료가 서로 다른 AnyIO worker thread에서 실행되어 기본 check_same_thread 제약에 걸렸다. 실제 예외 메시지에서 생성 thread와 사용 thread의 불일치를 확인했다.

## 해결

요청별 연결은 유지하며 check_same_thread=False를 설정했다. 데이터베이스 의존성은 scope="function"으로 지정하여 응답 전에 commit과 close를 완료한다. 테스트로 실제 브라우저의 가입·수정·즉시 새로고침 후 상태 보존을 확인했다.

## 다음 작업

영속성과 세션을 연결할 때 TestClient만으로 완료를 판단하지 않는다. 실제 서버에서 즉시 후속 요청과 새로고침을 확인한다. 전역 단일 DB 연결을 여러 요청에 공유하라는 의미는 아니다.
