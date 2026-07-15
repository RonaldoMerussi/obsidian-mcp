from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

from . import tools
from .auth import BearerAuthMiddleware
from .config import settings
from src import tools
from src.config import settings

mcp = FastMCP(
    "obsidian-tools",
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_host=[settings.allowed_host, "localhost:*", "127.0.0.1:*"],
        allowed_origins=[f"https://{settings.allowed_host}", "http://localhost:*"],
    ),
)

mcp.tool()(tools.search_notes)
mcp.tool()(tools.read_note)
mcp.tool()(tools.list_notes)
mcp.tool()(tools.write_note)
mcp.tool()(tools.replace_section)

app = mcp.streamable_http_app()
app = BearerAuthMiddleware(app)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=settings.port)
