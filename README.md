# Harness

재사용할 작업 규칙·문서·스킬과 **FastAPI + React·Vite** 기반 인증·업무 대시보드입니다.

## 실행

Docker와 Docker Compose 2.20 이상을 준비하고 실행합니다. 의존성 설치와 빌드는 자동으로 진행됩니다.

```sh
git clone https://github.com/elaus00/Harness.git
cd Harness
docker compose up --build -d --wait
```

[대시보드](http://127.0.0.1:8080) · [API 문서](http://127.0.0.1:8080/docs)

첫 접속 시 회원가입하세요. 종료는 `docker compose down`이며 저장된 데이터는 유지됩니다.

## 문서

- [실행·이용·테스트 안내](How_to_run.md)
- [작업 문서 색인](docs/index.md)
- [디자인 시스템](boilerplates/fastapi-react/DESIGN_SYSTEM.md)
