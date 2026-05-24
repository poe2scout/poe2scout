# [![](https://poe2scout.com/favicon.ico)](#) POE2 Scout

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

POE2 Scout is a market tool for Path of Exile 2 focused on real-time item and currency pricing. The repository is structured as a monorepo with separate application, backend package, and infrastructure boundaries.

## Repo Layout

- `apps/new-web`: React Router frontend served at `poe2scout.com`.
- `apps/web`: Legacy React frontend served at `old.poe2scout.com`.
- `apps/api`: API container definition.
- `apps/workers/item-sync`: Item sync worker container definition.
- `apps/workers/price-fetch`: Price fetch worker container definition.
- `apps/workers/currency-exchange`: Currency exchange worker container definition.
- `packages/backend`: Shared Python backend package used by the API and workers.
- `infra/compose`: Docker Compose files for local support services and production deployment.
- `infra/db`: PostgreSQL config and migrations.
- `infra/https-portal`: Production reverse-proxy templates.

## Local Development

### Prerequisites

- Docker
- Python 3.14.3
- [uv](https://docs.astral.sh/uv/)
- Node.js and npm

### Environment

Copy the root env example:

```bash
cp .env.example .env
```

### Start local infrastructure

This starts only PostgreSQL and Redis:

```bash
docker compose -f infra/compose/local.yml --env-file .env up -d
```

### Backend setup

```bash
cd packages/backend
uv sync
```

Run the API:

```bash
uv run uvicorn poe2scout.api.app:app --reload --app-dir src --port 5000
```

Run the workers manually when needed:

```bash
cd packages/backend
uv run python -m poe2scout.workers.item_sync
uv run python -m poe2scout.workers.price_fetch
uv run python -m poe2scout.workers.currency_exchange
```

### Frontend setup

```bash
cd apps/web
npm install
npm run dev
```

### Initial data flow

Run item sync first so the database has base data, then apply any required SQL migrations from `infra/db/migrations/legacy` if you need older manual bootstrap steps.

## Deployment

- Pushes to `main` build and publish container images to GHCR, including the new and legacy web images.
- Pushes to `release` also build and publish container images to GHCR, including the new and legacy web images.
- The new React Router frontend is also ready for Cloudflare Pages with root directory `apps/new-web`, build command `npm run build`, and output directory `build/client`.
- For Cloudflare Pages production, set `VITE_API_BASE_URL=https://api.poe2scout.com` and `API_ORIGIN=https://api.poe2scout.com`. `API_ORIGIN` is used only by the temporary `/api/*` compatibility proxy.
- After the `release` image workflow succeeds, a separate deploy workflow copies `infra/` and `.env` to the server and runs:
  `docker compose -f infra/compose/prod.yml -f infra/compose/observability.yml --env-file .env pull`
  followed by
  `docker compose -f infra/compose/prod.yml -f infra/compose/observability.yml --env-file .env up -d --remove-orphans`
- `poe2scout.com` serves the React Router web app, `old.poe2scout.com` serves the legacy web app, and `api.poe2scout.com` serves the canonical API.
- `poe2scout.com/api/*` is kept as a temporary compatibility route by the Cloudflare Pages Function in `apps/new-web/functions/api/[[path]].ts`; it strips `/api` and proxies to `api.poe2scout.com/*`.
- `beta.poe2scout.com` is kept in TLS routing and redirects to `poe2scout.com`.

## API

The public API is available at [api.poe2scout.com/swagger](https://api.poe2scout.com/swagger).

During the Cloudflare Pages migration, legacy `poe2scout.com/api/*` URLs continue to work through a temporary compatibility proxy. New clients should use `api.poe2scout.com/*`.

Please include a `User-Agent` with contact information if you are making sustained use of the API.

## Community

- Discord: [https://discord.gg/EHXVdQCpBq](https://discord.gg/EHXVdQCpBq)

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Disclaimer

POE2 Scout is an independent project and is not affiliated with or endorsed by Grinding Gear Games.
