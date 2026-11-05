.PHONY: install backend frontend check smoke e2e

install:
	cd backend && uv sync --locked
	cd frontend && npm ci

backend:
	cd backend && uv run --locked uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

frontend:
	cd frontend && npm run dev

check:
	cd backend && uv run --locked ruff check .
	cd backend && uv run --locked pytest
	cd frontend && npm run lint
	cd frontend && npm run build

smoke:
	python3 scripts/smoke.py

e2e:
	cd frontend && npm run test:e2e
