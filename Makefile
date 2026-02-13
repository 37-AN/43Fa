.PHONY: dev migrate seed test lint

dev:
	docker compose up --build

migrate:
	cd backend && alembic upgrade head

seed:
	cd backend && python -m app.seed

test:
	cd backend && pytest -q

lint:
	cd backend && ruff check . && black --check .
