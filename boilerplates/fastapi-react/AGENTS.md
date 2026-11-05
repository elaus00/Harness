# FastAPI + React + Vite starter

- 백엔드는 `backend/app`, 프론트엔드는 `frontend/src`에서 작업한다.
- API prefix는 `/api/v1`이다. 프론트엔드는 상대 경로 `/api/...`를 사용한다.
- 의존성 변경 시 `backend/uv.lock`, `frontend/package-lock.json`을 함께 갱신한다.
- 완료 전 이 폴더에서 `make check`를 실행한다.
- 실행과 배포 전제는 `README.md`를 따른다. 인증과 저장 구조는 README.md, 화면 규칙은 DESIGN_SYSTEM.md를 따른다.

- 인증·업무 흐름 변경 시 `make e2e`로 실제 브라우저 흐름을 검증한다.
