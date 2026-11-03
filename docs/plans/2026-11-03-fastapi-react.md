# FastAPI + React·Vite 기본형

사용자가 지정한 FastAPI와 React·Vite 구조를 `boilerplates/fastapi-react`에 설치한다. 공식 full-stack-fastapi-template 전체 도입은 인증·DB 설정까지 포함하므로, 기본형은 공식 Vite react-ts 생성기와 독립 FastAPI 앱으로 구성한다.

- [x] Python 3.12/uv 백엔드와 health API·테스트
- [x] 공식 create-vite@9.3.3 기반 React·TypeScript 프론트엔드
- [x] 의존성 설치와 잠금 파일
- [x] 개발용 API 프록시·오류 상태·재시도·5초 제한
- [x] 실행 명령·새 프로젝트 복사·운영 전제 문서
- [x] lint·API 테스트·타입 검사·빌드
- [x] 실제 HTTP 서버와 프록시 통합 검증

외부 저장소의 애플리케이션을 통째로 복제하지 않았다. DB·인증·배포는 이번 설치 범위 밖이다.

## 검증 결과

2026-11-03: Ruff·프론트엔드 lint·TypeScript/Vite 빌드 통과. API 테스트 3개는 경고를 오류로 처리해도 통과. 실제 서버 HTTP 검증에서 health·Vite HTML·API 프록시 연결 통과. 검증용 서버는 자동 종료했다. 브라우저 클릭 테스트와 운영 배포는 수행하지 않았다.

설치 버전: Python 3.12.7, FastAPI 0.162.0, React 19.3.1, Vite 8.3.5. 의존성은 uv.lock/package-lock.json에 기록했다.
