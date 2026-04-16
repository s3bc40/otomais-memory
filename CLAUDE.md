# Les Mémoires d'Otomaï

Web encyclopedia of Dofus game equipment.
This is the core of a larger application — DRF, MCP server integration, and AI capabilities
will be added incrementally. Keep architecture decisions open to those additions.

## Commands

- Install dependencies: `uv sync`
- Start dev server: `uv run python manage.py runserver`
- Migrations: `uv run python manage.py makemigrations && uv run python manage.py migrate`
- Tests: `uv run pytest`
- Lint: `uv run ruff check . && uv run ruff format --check .`
- Type check: `uv run mypy .`

## Stack

- Python 3.12+, managed with uv
- Django 5.2 LTS
- Database: SQLite in dev, PostgreSQL in prod
- Tests: pytest + pytest-django

## Conventions

- All views use class-based views (CBV)
- App URLs live in `encyclopedia/urls.py`, included from `otomais/urls.py`
- Models always define `__str__` and `class Meta` with `verbose_name`
- No business logic in views — it goes in services (`encyclopedia/services/`)
- Sensitive environment variables are read via `python-decouple` (`.env` file)
- Never commit `SECRET_KEY` or credentials to version control
