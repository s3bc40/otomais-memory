# Transport roadmap:
#   stdio            — local dev and Claude Code integration (current)
#   streamable-http  — AWS ECS deployment (one-line swap):
#                      mcp.run(transport='streamable-http', host='0.0.0.0', port=8001)
# Tool and resource logic is identical across transports.

import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("otomais")

BASE_URL = "http://127.0.0.1:8000"
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


@mcp.tool()
async def search_equipment(name: str, type_id: int | None = None) -> str:
    """
    Search Dofus equipment by name, optionally filtered by item type.

    Use this when the user asks to find equipment by name. For full stats on a
    specific result, follow up with get_equipment_detail. If you need a type_id,
    read the equipment://types resource first.

    Args:
        name: Partial or full equipment name (case-insensitive).
        type_id: ankama_id of the item type to filter by (optional).

    Returns: Markdown list of matches (ankama_id, name, level, type, icon URL),
             "No equipment found." if empty, or an error string on failure.
    """
    params: dict = {"q": name}
    if type_id is not None:
        params["type"] = type_id
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        r = await client.get(f"{BASE_URL}/api/equipment/", params=params)
    if r.status_code != 200:
        return f"Error {r.status_code}: search failed."
    items = r.json().get("results", [])
    if not items:
        return "No equipment found."
    lines = [
        f"- **{i['name']}** (lvl {i['level']}) — {i['item_type']['name']}"
        f" | ankama_id: {i['ankama_id']} | icon: {i['image_icon_url']}"
        for i in items
    ]
    return "\n".join(lines)


@mcp.tool()
async def get_equipment_detail(ankama_id: int) -> str:
    """
    Get full details for a single piece of Dofus equipment by its ankama_id.

    Use this after search_equipment to retrieve the description and SD image URL.
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
    return (
        f"**{d['name']}** (lvl {d['level']})\n"
        f"Type: {d['item_type']['name']}\n"
        f"Description: {d.get('description') or '—'}\n"
        f"Image: {d.get('image_sd_url') or '—'}\n"
        f"ankama_id: {d['ankama_id']}"
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")
