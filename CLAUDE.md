# Les Mémoires d'Otomaï

Web encyclopedia of Dofus game equipment.
This is the core of a larger application — DRF, MCP server integration, and AI capabilities
will be added incrementally. Keep architecture decisions open to those additions.

## Commands

- Install dependencies: `uv sync`
- Start dev server: `uv run python manage.py runserver`
- Migrations: `uv run python manage.py makemigrations && uv run python manage.py migrate`
- Sync equipment data: `uv run python manage.py sync_equipment`
- Sync set data: `uv run python manage.py sync_sets`
- Tests: `uv run pytest`
- Lint: `uv run ruff check . && uv run ruff format --check .`
- Type check: `uv run mypy .`

## Stack

- Python 3.12+, managed with uv
- Django 5.2 LTS
- Database: SQLite in dev, PostgreSQL in prod
- Tests: pytest + pytest-django
- HTTP client: httpx
- Env vars: environs (`env.str`, `env.bool`, etc.) — reads from `.env` via `env.read_env()`
- Container: Docker + docker compose (local dev), Gunicorn (prod entrypoint)

## Environment variables

Copy `.env.example` to `.env` and fill in values. Required variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | — (required) | Django secret key |
| `DEBUG` | `False` | Enable debug mode |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | Comma-separated allowed hosts |
| `DATABASE_URL` | `sqlite:///db.sqlite3` | Database URL (SQLite or PostgreSQL) |
| `MCP_BASE_URL` | `http://127.0.0.1:8000` | Django API base URL for the MCP server |
| `MCP_HOST` | `127.0.0.1` | Host to bind for HTTP transport |
| `MCP_TRANSPORT` | `stdio` | MCP transport: `stdio` (local) or `http` (remote) |
| `MCP_PORT` | `8001` | Port for HTTP transport |

PostgreSQL example: `DATABASE_URL=postgres://user:password@host:5432/dbname`

## Container setup

```bash
# Copy and edit env file
cp .env.example .env

# Build and start (live reload, SQLite)
docker compose up --build

# App available at http://localhost:8000
```

The docker compose setup mounts the source directory so code changes are reflected without rebuilding.

For production (EC2 + PostgreSQL), set `DATABASE_URL` to a PostgreSQL URL, `DEBUG=False`, and update `SECRET_KEY` and `ALLOWED_HOSTS`. The same image uses Gunicorn as entrypoint.

## Data sync

`sync_equipment` fetches all equipment from dofusdude in a single gzip request and upserts Equipment + EquipmentEffect rows.
`sync_sets` fetches all sets and upserts Set + SetEffect rows. Set effects are keyed by pieces count (e.g. "2", "3") in the API response.

Two perf decisions to keep:
- `transaction.atomic()` wraps the entire loop — avoids one disk flush per query on SQLite (193s → ~5s)
- `ItemType` is loaded into a dict before the loop — avoids ~4 350 `get_or_create` DB hits at runtime

## Testing

Tests live in `encyclopedia/tests/` (one file per source file). Shared fixtures are in `conftest.py`.
No real HTTP calls — mock `httpx.get` at the module level with `unittest.mock.patch`.
CI runs on every push and PR to `main` via `.github/workflows/ci.yml` (lint → format check → pytest).

## MCP Server

The MCP server at `mcp_server/server.py` exposes the encyclopedia via httpx calls to the DRF API.
Transport is env-var driven (`MCP_TRANSPORT`): `stdio` for local Claude Code (default), `streamable-http` for remote deploys (Pi via Tailscale). `MCP_PORT` defaults to `8001`.

Two config files at repo root:
- `.mcp.json` — stdio, default local, committed
- `.mcp.remote.json` — streamable-http example (Pi via Tailscale or future remote deploy); copy to `.mcp.json` and update the URL to switch

Run locally (requires dev server at `http://127.0.0.1:8000`):
```bash
uv run python mcp_server/server.py
```

### Resources

| URI | Description |
|-----|-------------|
| `equipment://types` | All ItemType records — read before filtering search by type |
| `sets://all` | All Set records ordered by level asc |

### Tools

| Tool | Parameters | Description |
|------|-----------|-------------|
| `search_equipment` | `name`, `type_id?`, `is_weapon?` | Search equipment by name. Returns enriched list with effects, pods, weapon flag, and set name. |
| `get_equipment_detail` | `ankama_id` | Full detail: all images, weapon stats, effects, recipe, conditions, set info. |
| `search_sets` | `query`, `min_level=0`, `max_level=200` | Search sets by name with level range. Effects grouped by pieces count. |
| `get_set_detail` | `ankama_id` | Full set detail including resolved equipment list with effects. |

## Workflow

At the end of each completed step, always write a PM report covering: what changed, the commit hash, test results, and any notable decisions or bugs fixed.

## Conventions

- All views use class-based views (CBV)
- App URLs live in `encyclopedia/urls.py`, included from `otomais/urls.py`
- Models always define `__str__` and `class Meta` with `verbose_name`
- No business logic in views — it goes in services (`encyclopedia/services/`)
- Sensitive environment variables are read via `environs` (`.env` file)
- Never commit `SECRET_KEY` or credentials to version control
