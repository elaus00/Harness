# Starlette TestClient의 HTTP 클라이언트 확인

날짜: 2026-11-03. 적용 범위: 이번 잠금 파일의 FastAPI 0.162.0 / Starlette 1.10.0.

## 관찰과 근거

기존 방식으로 httpx 0.28.1을 설치하니 API 테스트는 통과했으나 StarletteDeprecationWarning이 발생했다. 설치된 starlette/testclient.py는 httpx2를 먼저 가져오고 httpx로 대체되면 경고한다. [공식 문서](https://starlette.dev/testclient/)에서도 httpx2 기반 테스트 클라이언트를 확인했다.

## 해결과 검증

개발 의존성의 httpx를 제거하고 httpx2 2.16.0을 설치해 uv.lock을 갱신했다. `uv run --locked pytest -W error`에서 테스트 3개가 통과했다. 경고를 숨긴 우회책이 아닌 권장 의존성으로 전환했다.

## 다음에 적용

최신 FastAPI 테스트 환경을 만들 때 과거 예제만 보고 HTTP 클라이언트를 고정하지 않는다. 설치된 Starlette 버전과 실제 경고, 해당 버전 문서를 확인한다. 이전 버전까지 일괄 전환하라는 규칙은 아니다.
