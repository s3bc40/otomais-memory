# Les Mémoires d'Otomaï

Web encyclopedia of Dofus game equipment.
This is the core of a larger application — DRF, MCP server integration, and AI capabilities
will be added incrementally. Keep architecture decisions open to those additions.

## Commands

- Install dependencies: `uv sync`
- Start dev server: `uv run python manage.py runserver`
- Migrations: `uv run python manage.py makemigrations && uv run python manage.py migrate`
- Sync equipment data: `uv run python manage.py sync_equipment`
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

## Data sync

`sync_equipment` fetches all equipment from dofusdude in a single gzip request and upserts Equipment + EquipmentEffect rows.

Two perf decisions to keep:
- `transaction.atomic()` wraps the entire loop — avoids one disk flush per query on SQLite (193s → ~5s)
- `ItemType` is loaded into a dict before the loop — avoids ~4 350 `get_or_create` DB hits at runtime

## Conventions

- All views use class-based views (CBV)
- App URLs live in `encyclopedia/urls.py`, included from `otomais/urls.py`
- Models always define `__str__` and `class Meta` with `verbose_name`
- No business logic in views — it goes in services (`encyclopedia/services/`)
- Sensitive environment variables are read via `environs` (`.env` file)
- Never commit `SECRET_KEY` or credentials to version control
