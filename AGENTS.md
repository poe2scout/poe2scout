# Repository Guidelines

POE2 Scout combines FastAPI services, background workers, and a Vite/React client. Use these notes to stay aligned with the layout.

## Project Structure & Module Organization
- `services/apiService/` hosts the public FastAPI app; routers sit in `routes/` and shared helpers under `services/libs/`.
- `services/itemSyncService/` and `services/priceFetchService/` provide scheduled ingestion; the data access layer (DAL) lives in `services/repositories/`.
- `frontend/vite-project/` contains the Vite + React UI (`src/` code, `public/` assets, `dist/` builds).
- `db/migrations/` stores SQL migration scripts to apply after item sync runs or schema changes; `docker-compose.yml` spins up PostgreSQL for local work, while `https-portal/` stays production-only.

## Build, Test, and Development Commands
- Backend setup: `uv pip install -r requirements.txt` inside an activated `.venv`.
- Start data services: `docker-compose up -d` for PostgreSQL, then `python -m services.itemSyncService` to populate base items and apply `db/migrations/PostItemSyncService.sql`.
- Serve the API with `uvicorn services.apiService.app:app --reload --port 5000` (set `LOCAL=true` for relaxed CORS).
- Frontend loop: `cd frontend/vite-project && npm install && npm run dev`; build and lint with `npm run build` and `npm run lint`.

## Coding Style & Naming Conventions
- Python uses Ruff (`pypproject.toml`): 4-space indent, 88-character limit, double quotes; favour type hints and snake_case functions/classes in PascalCase.
- Run `ruff check services` before pushing; keep async code non-blocking and log through the shared logger.
- React/TypeScript follows the ESLint config: components named in PascalCase, hooks prefixed with `use`, shared utilities in `src/utils/`.

## Testing Guidelines
- We have minimal automated coverage—add `pytest` suites under `services/<module>/tests/` named `test_*.py`, and run them with `pytest` from the repo root.
- Exercise new routes with FastAPI’s `TestClient` and seed test data via SQL fixtures or temporary tables.
- For frontend updates, pair visual validation in `npm run dev` with `@testing-library/react` checks.

## Commit & Pull Request Guidelines
- Match the existing concise, present-tense summaries (`Added logging…`, `Ensures only exalted…`); prefix scope (`api:`, `frontend:`) when helpful.
- Separate behaviour from formatting (e.g., a dedicated `formats code` commit) to simplify reviews.
- PRs should outline environment impacts, migrations, and UI changes—link issues, attach screenshots for visual tweaks, and list commands/tests executed.

## Configuration & Security Notes
- Copy `.env.example` to `.env`; populate `DBSTRING`, `SECRET_KEY`, POE API credentials, and `LOCAL` as needed. Never commit secrets.
- Production deploys run from the `release` branch via `.github/workflows/push_to_prod.yaml`; coordinate merges accordingly.
- Keep generated data (`dump.rdb`, build artifacts) outside version control or within ignored paths.
