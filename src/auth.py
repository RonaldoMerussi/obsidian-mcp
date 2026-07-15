from starlette.types import ASGIApp, Receive, Scope, Send
from starlette.responses import PlainTextResponse
import secrets

from .config import settings


class BearerAuthMiddleware:
    """Rejects any request missing a valid `Authorization: Bearer <token>` header."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = dict(scope["headers"])
        auth_header = headers.get(b"authorization", b"").decode()
        expected = f"Bearer {settings.mcp_auth_token}"

        if not secrets.compare_digest(auth_header, expected):
            response = PlainTextResponse("Unauthorized", status_code=401)
            await response(scope, receive, send)
            return

        await self.app(scope, receive, send)
