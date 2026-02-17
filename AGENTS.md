# Repository Guidelines

## Project Structure & Module Organization
- `backend/`: FastAPI service.
- `backend/app/`: core application code.
- `backend/app/domain`: entities and analytics logic.
- `backend/app/application`: use cases and DTOs.
- `backend/app/infrastructure`: DB, repos, security, logging, metrics.
- `backend/app/api`: routers, schemas, and dependencies.
- `backend/tests/`: backend tests.
- `backend/alembic/`: database migrations.
- `backend/sample_data/`: CSVs for demos.
- `frontend/`: Vue app.
- `frontend/src/`: UI source code (`components/`, `views/`, `api/`, `router/`).
- `frontend/public/`: static assets.

## Build, Test, and Development Commands
- `make dev`: build and start the full stack with Docker Compose.
- `make migrate`: apply Alembic migrations to the database.
- `make seed`: generate 6 months of synthetic data.
- `make test`: run backend tests (`pytest -q`).
- `make lint`: run backend lint/format checks (`ruff`, `black --check`).
- `cd frontend && npm run dev`: run the UI locally on `:5173`.
- `cd frontend && npm run build`: type-check and build the UI bundle.
- `cd frontend && npm run lint`: run ESLint on the UI.

## Coding Style & Naming Conventions
- Python formatting is enforced by Black and Ruff with 100-char lines.
- Favor `snake_case` for Python modules/functions and `PascalCase` for classes.
- Vue components follow existing file naming patterns in `frontend/src/components/`.
- Keep config in `.env` (start from `.env.example`) and avoid hardcoding secrets.

## Testing Guidelines
- Backend tests live under `backend/tests/` and run with `pytest`.
- Follow existing test naming patterns in that folder (typically `test_*.py`).
- No dedicated frontend test runner is configured; keep UI changes covered by manual checks.

## Commit & Pull Request Guidelines
- This directory is not a Git checkout, so commit message conventions are unknown.
- When opening PRs, include a concise summary, the commands you ran, and screenshots
  for UI changes. Link related issues when applicable.

## Security & Configuration Tips
- Default users are `admin/admin123` and `viewer/viewer123` (local MVP only).
- The API serves docs at `/docs`, and the frontend proxies `/api/*` during dev.
