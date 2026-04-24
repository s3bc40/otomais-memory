# Transport is env-var driven (twelve-factor):
#   MCP_TRANSPORT=stdio            — local dev and Claude Code integration (default)
#   MCP_TRANSPORT=http             — remote deploy (Pi via Tailscale, AWS)
# Tool and resource logic is identical across transports.

from pathlib import Path
import httpx
from environs import Env
from fastmcp import FastMCP

env = Env()
env.read_env(Path(__file__).resolve().parent.parent / ".env")

transport = env.str("MCP_TRANSPORT", "stdio")
host = env.str("MCP_HOST", "127.0.0.1")
port = env.int("MCP_PORT", 8001)

mcp = FastMCP("otomais")

BASE_URL = env.str("MCP_BASE_URL", "http://127.0.0.1:8000")
TIMEOUT = 10.0


@mcp.resource("equipment://types")
async def equipment_types() -> str:
    """All Dofus item types with their ankama_id. Read this before filtering a search by type."""
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        r = await client.get(f"{BASE_URL}/api/item-types/")
    if r.status_code != 200:
        return f"Error {r.status_code}: could not load item types."
    # ItemTypeViewSet has pagination_class = None — response is a plain list, not {"results": [...]}
    types: list[dict] = r.json()
    return "\n".join(f"{t['ankama_id']} — {t['name']}" for t in types)


@mcp.resource("sets://all")
async def all_sets() -> str:
    """All Dofus sets ordered by level ascending. Browse this before searching to see what's available."""
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        r = await client.get(f"{BASE_URL}/api/sets/")
    if r.status_code != 200:
        return f"Error {r.status_code}: could not load sets."
    sets = r.json().get("results", [])
    if not sets:
        return "No sets found."
    return "\n".join(
        f"- **{s['name']}** (lvl {s['level']}) | ankama_id: {s['ankama_id']}"
        f" | items: {s['items_count']} | cosmetics: {s['contains_cosmetics']}"
        for s in sets
    )


@mcp.tool()
async def search_equipment(
    name: str,
    type_id: int | None = None,
    is_weapon: bool | None = None,
) -> str:
    """
    Search Dofus equipment by name, optionally filtered by item type and/or weapon status.

    Use this when the user asks to find equipment by name. For full stats on a
    specific result, follow up with get_equipment_detail. If you need a type_id,
    read the equipment://types resource first.

    Args:
        name: Partial or full equipment name (case-insensitive).
        type_id: ankama_id of the item type to filter by (optional).
        is_weapon: True to return only weapons, False for non-weapons, None for all (optional).

    Returns: Markdown list of matches, "No equipment found." if empty, or an error string on failure.
    """
    params: dict = {"q": name}
    if type_id is not None:
        params["type"] = type_id
    if is_weapon is not None:
        params["is_weapon"] = str(is_weapon).lower()
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        r = await client.get(f"{BASE_URL}/api/equipment/", params=params)
    if r.status_code != 200:
        return f"Error {r.status_code}: search failed."
    items = r.json().get("results", [])
    if not items:
        return "No equipment found."
    lines = []
    for i in items:
        effects_str = ", ".join(i["effects"]) if i["effects"] else "—"
        line = (
            f"- **{i['name']}** (lvl {i['level']}) — {i['item_type']['name']}"
            f" | ankama_id: {i['ankama_id']} | weapon: {i['is_weapon']}"
            f" | pods: {i['pods'] if i['pods'] is not None else '—'}"
            f" | effects: {effects_str}"
            f" | icon: {i['image_icon_url']}"
        )
        if i.get("parent_set_name"):
            line += f" | set: {i['parent_set_name']}"
        lines.append(line)
    return "\n".join(lines)


@mcp.tool()
async def get_equipment_detail(ankama_id: int) -> str:
    """
    Get full details for a single piece of Dofus equipment by its ankama_id.

    Use this after search_equipment to retrieve all stats, effects, and set info.
    Do not guess ankama_id values — always obtain them from search_equipment first.

    Args:
        ankama_id: The equipment's Dofus ankama_id (integer from search results).

    Returns: Formatted markdown detail block, or an error string if not found.
    """
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        r = await client.get(f"{BASE_URL}/api/equipment/{ankama_id}/")
    if r.status_code == 404:
        return f"Equipment ankama_id {ankama_id} not found."
    if r.status_code != 200:
        return f"Error {r.status_code}: could not retrieve equipment."
    d = r.json()

    effects_lines = "\n".join(f"  - {e['formatted']}" for e in d.get("effects", []))
    effects_block = effects_lines or "  — (no effects)"

    weapon_block = ""
    if d.get("is_weapon"):
        weapon_block = (
            f"\nCritical hit probability: {d.get('critical_hit_probability') or '—'}"
            f"\nCritical hit bonus: {d.get('critical_hit_bonus') or '—'}"
            f"\nMax cast per turn: {d.get('max_cast_per_turn') or '—'}"
            f"\nAP cost: {d.get('ap_cost') or '—'}"
            f"\nRange: {d.get('range_min') or '—'} – {d.get('range_max') or '—'}"
        )

    set_block = ""
    if d.get("parent_set_id"):
        set_block = f"\nSet: {d['parent_set_name']} (ankama_id: {d['parent_set_id']})"

    return (
        f"**{d['name']}** (lvl {d['level']})\n"
        f"Type: {d['item_type']['name']} | Weapon: {d.get('is_weapon')} | Pods: {d.get('pods') or '—'}\n"
        f"Description: {d.get('description') or '—'}\n"
        f"Images:\n"
        f"  icon: {d.get('image_icon_url') or '—'}\n"
        f"  sd: {d.get('image_sd_url') or '—'}\n"
        f"  hq: {d.get('image_hq_url') or '—'}\n"
        f"  hd: {d.get('image_hd_url') or '—'}"
        f"{weapon_block}"
        f"{set_block}\n"
        f"Effects:\n{effects_block}\n"
        f"Recipe: {d.get('recipe') or '—'}\n"
        f"Conditions: {d.get('conditions') or '—'}\n"
        f"ankama_id: {d['ankama_id']}"
    )


@mcp.tool()
async def search_sets(
    query: str,
    min_level: int = 0,
    max_level: int = 200,
) -> str:
    """
    Search Dofus sets by name, optionally filtered by level range.

    Use this when the user asks about sets. For full set details and equipment list,
    follow up with get_set_detail. Browse sets://all to see all available sets.

    Args:
        query: Partial or full set name (case-insensitive).
        min_level: Minimum set level inclusive (default 0).
        max_level: Maximum set level inclusive (default 200).

    Returns: Markdown list of matching sets with effects grouped by pieces count,
             "No sets found." if empty, or an error string on failure.
    """
    params: dict = {"q": query, "min_level": min_level, "max_level": max_level}
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        r = await client.get(f"{BASE_URL}/api/sets/", params=params)
    if r.status_code != 200:
        return f"Error {r.status_code}: search failed."
    sets = r.json().get("results", [])
    if not sets:
        return "No sets found."
    lines = []
    for s in sets:
        effects_str = _format_effects_by_pieces(s.get("effects_by_pieces", {}))
        lines.append(
            f"- **{s['name']}** (lvl {s['level']}) | ankama_id: {s['ankama_id']}"
            f" | items: {s['items_count']}\n"
            f"  Effects by pieces:\n{effects_str}"
        )
    return "\n".join(lines)


@mcp.tool()
async def get_set_detail(ankama_id: int) -> str:
    """
    Get full details for a Dofus set by its ankama_id, including all equipment in the set.

    Do not guess ankama_id values — always obtain them from search_sets first.

    Args:
        ankama_id: The set's Dofus ankama_id (integer from search_sets results).

    Returns: Formatted markdown detail block with set effects and equipment list,
             or an error string if not found.
    """
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        r = await client.get(f"{BASE_URL}/api/sets/{ankama_id}/")
    if r.status_code == 404:
        return f"Set ankama_id {ankama_id} not found."
    if r.status_code != 200:
        return f"Error {r.status_code}: could not retrieve set."
    s = r.json()

    # Detail endpoint returns flat effects list with pieces_count per item
    effects_str = _format_effects_by_pieces(
        _group_effects_by_pieces(s.get("effects", []))
    )

    eq_lines = []
    for eq in s.get("equipment_list", []):
        eq_effects = ", ".join(eq["effects"]) if eq["effects"] else "—"
        eq_lines.append(
            f"  - **{eq['name']}** (lvl {eq['level']}) | {eq['item_type']['name']}"
            f" | weapon: {eq['is_weapon']} | ankama_id: {eq['ankama_id']}\n"
            f"    effects: {eq_effects}"
        )
    equipment_str = "\n".join(eq_lines) if eq_lines else "  — (no equipment found)"

    return (
        f"**{s['name']}** (lvl {s['level']})\n"
        f"ankama_id: {s['ankama_id']} | items: {s['items_count']}"
        f" | contains_cosmetics: {s['contains_cosmetics']}"
        f" | contains_cosmetics_only: {s['contains_cosmetics_only']}\n"
        f"Effects by pieces:\n{effects_str}\n"
        f"Equipment in set:\n{equipment_str}"
    )


def _group_effects_by_pieces(effects: list[dict]) -> dict[int, list[str]]:
    grouped: dict[int, list[str]] = {}
    for e in effects:
        grouped.setdefault(e["pieces_count"], []).append(e["formatted"])
    return grouped


def _format_effects_by_pieces(grouped: dict[int, list[str]]) -> str:
    if not grouped:
        return "    — (no effects)"
    return "\n".join(
        f"    {count} pieces: {', '.join(grouped[count])}" for count in sorted(grouped)
    )


if __name__ == "__main__":
    if transport != "stdio":
        print(f"Starting MCP server ({transport}) on {host}:{port}")
        mcp.run(transport=transport, host=host, port=port)
    else:
        print("Starting MCP server (stdio)")
        mcp.run(transport="stdio")
