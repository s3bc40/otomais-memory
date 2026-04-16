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

## Roadmap

- [ ] Equipment data model and admin interface
- [ ] Browse and search encyclopedia views
- [ ] REST API (Django REST Framework)
- [ ] MCP server integration
- [ ] AI-powered features
