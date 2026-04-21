# Les Mémoires d'Otomaï

A web encyclopedia of equipment from the game [Dofus](https://www.dofus.com), named after the NPC Otomaï.

## Goal

Provide a comprehensive, browsable reference for all in-game equipment: weapons, gear, sets, and their stats. Built to serve as the data core of a larger application with an API layer, AI capabilities, and MCP server integration planned incrementally.

## Stack

- **Python 3.12+** managed with [uv](https://docs.astral.sh/uv/)
- **Django 5.2 LTS**
- **SQLite** (dev) / **PostgreSQL** (prod)

## Getting started

```bash
# Install dependencies
uv sync

# Apply migrations
uv run python manage.py migrate

# Start the development server
uv run python manage.py runserver
```

## Development

```bash
# Run tests
uv run pytest

# Lint and format
uv run ruff check .
uv run ruff format .
```

## Data sync

Equipment data is sourced from [dofusdude](https://docs.dofusdu.de/) via a single gzip-compressed request to the `/all` endpoint.

```bash
uv run python manage.py sync_equipment
```

Syncs ~4 350 items and ~27 000 effects in under 10 seconds. The command is idempotent — safe to re-run at any time.

## Roadmap

- [x] Equipment model, migration, and admin interface
- [x] Browse and search encyclopedia views
- [x] REST API (Django REST Framework)
- [x] `sync_equipment` — full field mapping + EquipmentEffect sync
- [x] MCP server — stdio transport, local Claude Code integration
- [ ] Tests — pytest-django: models, sync, DRF API client
- [ ] Set + SetEffect models, migration, and `sync_sets` command
- [ ] Dockerfile + docker-compose local stack
- [ ] Serializers updated for sets and effects
- [ ] MCP tools updated for sets + cloud deployment (AWS ECS / streamable-http)
- [ ] Architecture diagram + final README
