# Les Mémoires d'Otomaï

A web encyclopedia of equipment from the game [Dofus](https://www.dofus.com), named after the NPC Otomaï.

## Goal

Provide a comprehensive, browsable reference for all in-game equipment: weapons, gear, sets, and their stats. Built to serve as the data core of a larger application with an API layer, AI capabilities, and MCP server integration planned incrementally.

## Stack

- **Python 3.12+** managed with [uv](https://docs.astral.sh/uv/)
- **Django 5.2 LTS**
- **SQLite** (dev) / **PostgreSQL** (prod)

## Getting started

### With Docker (recommended)

```bash
# Copy and configure environment
cp .env.example .env

# Build and start (SQLite, live reload)
docker compose up --build
```

App is available at <http://localhost:8000>.

Code changes are reflected immediately — no rebuild needed.

### Without Docker

```bash
# Install dependencies
uv sync

# Copy and configure environment
cp .env.example .env

# Run this one liner cmd to generate your local secret key and add to your .env
uv run python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

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

## REST API

Base URL: `http://localhost:8000/api/`

| Endpoint | Description |
|---|---|
| `GET /api/equipment/` | Paginated equipment list. Supports `?q=name`, `?type=<ankama_id>`, `?is_weapon=true\|false`. |
| `GET /api/equipment/<ankama_id>/` | Full equipment detail with effects, weapon stats, recipe, and conditions. |
| `GET /api/item-types/` | All item types (unpaginated). |
| `GET /api/sets/` | Paginated set list. Supports `?q=name`, `?level=<level>`, `?min_level=<n>`, `?max_level=<n>`. |
| `GET /api/sets/<ankama_id>/` | Full set detail with effects grouped by pieces count and resolved equipment list. |

All list endpoints return 24 results per page. Navigate with `?page=2`.

## Data sync

Equipment and set data are sourced from [dofusdude](https://docs.dofusdu.de/) via single gzip-compressed requests to the `/all` endpoints.

```bash
uv run python manage.py sync_equipment
uv run python manage.py sync_sets
```

Both commands are idempotent — safe to re-run at any time. `sync_equipment` syncs ~4 350 items and ~27 000 effects in under 10 seconds.

## MCP server

The MCP server exposes equipment search and detail tools over **stdio**, allowing Claude Code to query the encyclopedia directly.

### Run locally

Both the Django app and the MCP server must be running at the same time.

```bash
# Terminal 1 — Django REST API (MCP server calls this)
uv run python manage.py runserver

# Terminal 2 — MCP server (stdio transport)
uv run python mcp_server/server.py
```

The `.mcp.json` at the repo root registers the server automatically with Claude Code. Once both processes are up, open Claude Code in this directory and the `otomais` tools will be available.

### Inspect with MCP Inspector

[MCP Inspector](https://github.com/modelcontextprotocol/inspector) is an interactive browser UI for testing tools and resources manually without involving Claude.

```bash
# Terminal 1 — Django REST API must be running first
uv run python manage.py runserver

# Terminal 2 — launch the inspector UI (opens http://localhost:6274)
npx @modelcontextprotocol/inspector
```

In the inspector UI, set the command to `uv run python mcp_server/server.py` and click **Connect**. Then:

1. Under **Resources**, click `equipment://types` to verify item types load.
2. Under **Tools**, call `search_equipment` with `{"name": "gelano"}` to test search.
3. Call `get_equipment_detail` with the `ankama_id` returned from the search.
4. Call `search_sets` with `{"query": "bouftou"}` to verify grouped effects.
5. Call `get_set_detail` with the `ankama_id` to verify the equipment list.

### Available tools and resources

| Name | Type | Description |
|---|---|---|
| `equipment://types` | Resource | All item types with their `ankama_id`. Read before filtering by type. |
| `sets://all` | Resource | All sets ordered by level. Browse before searching. |
| `search_equipment` | Tool | Search equipment by name. Optional `type_id` and `is_weapon` filters. Returns effects, pods, set name. |
| `get_equipment_detail` | Tool | Full detail for a single item: all images, weapon stats, effects, recipe, conditions. |
| `search_sets` | Tool | Search sets by name with optional `min_level`/`max_level`. Returns effects grouped by pieces count. |
| `get_set_detail` | Tool | Full set detail including resolved equipment list with effects. |

## Roadmap

- [x] Equipment model, migration, and admin interface
- [x] Browse and search encyclopedia views
- [x] REST API (Django REST Framework)
- [x] `sync_equipment` — full field mapping + EquipmentEffect sync
- [x] MCP server — stdio transport, local Claude Code integration
- [x] Tests — pytest-django: models, sync, DRF API client
- [x] Set + SetEffect models, migration, and `sync_sets` command
- [x] Dockerfile + docker-compose local stack
- [x] Sets API — list + detail endpoints with nested effects
- [x] MCP tools updated for sets — search_sets, get_set_detail, sets://all resource
- [ ] Architecture diagram + final README
