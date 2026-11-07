"""mcp-redis over Streamable HTTP with a bearer token, for a Gateway upstream behind a tunnel.
mcp-redis 0.5.1 only runs stdio from its CLI; this imports its FastMCP server and serves HTTP.
usage: MCP_TOKEN=... MCP_PUBLIC_HOST=mcp-lab.example.dev .venv/bin/python serve_http.py
env: REDIS_URL (default redis://127.0.0.1:26379/0), MCP_PORT (default 28090)
"""
import os
import secrets

import uvicorn
from mcp.server.transport_security import TransportSecuritySettings
from src.common.config import parse_redis_uri, set_redis_config_from_cli
from src.common.server import mcp

set_redis_config_from_cli(parse_redis_uri(os.environ.get("REDIS_URL", "redis://127.0.0.1:26379/0")))
token = os.environ["MCP_TOKEN"]
public = os.environ["MCP_PUBLIC_HOST"]
mcp.settings.transport_security = TransportSecuritySettings(
    enable_dns_rebinding_protection=True,
    allowed_hosts=[public, "127.0.0.1:*", "localhost:*"],
    allowed_origins=[f"https://{public}"],
)
app = mcp.streamable_http_app()


async def bearer(scope, receive, send):
    if scope["type"] == "http":
        auth = dict(scope["headers"]).get(b"authorization", b"").decode()
        ok = secrets.compare_digest(auth, f"Bearer {token}")
        print(f"{scope['method']} {scope['path']} auth={'ok' if ok else 'refused'}", flush=True)
        if not ok:
            await send({"type": "http.response.start", "status": 401, "headers": [(b"content-type", b"text/plain")]})
            await send({"type": "http.response.body", "body": b"unauthorized"})
            return
    await app(scope, receive, send)


uvicorn.run(bearer, host="127.0.0.1", port=int(os.environ.get("MCP_PORT", "28090")), log_level="warning")
