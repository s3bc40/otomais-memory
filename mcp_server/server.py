# Transport roadmap:
#   stdio            — local dev and Claude Code integration (current)
#   streamable-http  — AWS ECS deployment (one-line swap):
#                      mcp.run(transport='streamable-http', host='0.0.0.0', port=8001)
# Tool and resource logic is identical across transports.

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("otomais")


if __name__ == "__main__":
    mcp.run(transport="stdio")
