import asyncio
from pathlib import Path
from typing import Callable
import urllib.parse

import slash.logging

from aiohttp import WSMsgType, web

PATH_PUBLIC = Path("../public")

ALLOWED_MIME_TYPES = {
    ".html": "text/html",
    ".css": "text/css",
    ".js": "text/javascript",
    ".png": "image/png",
    ".ttf": "font/ttf",
}


class Server:
    def __init__(self, host: str, port: int) -> None:
        self._host = host
        self._port = port
        self._logger = slash.logging.create_logger()
        self._ws_clients: set[web.WebSocketResponse] = set()
        self._ws_connect_callback: Callable[[], list[str]] | None = None
        self._ws_message_callback: Callable[[str], list[str]] | None = None

    def on_ws_connect(self, callback: Callable[[], list[str]]) -> None:
        self._ws_connect_callback = callback

    def on_ws_message(self, callback: Callable[[str], list[str]]) -> None:
        self._ws_message_callback = callback

    def serve(self) -> None:
        self._logger.info(f"Serving on http://{self._host}:{self._port} ..")

        self.app = web.Application()
        self.app.router.add_get("/ws", self._ws_handler)
        self.app.router.add_route("*", "/{tail:.*}", self._http_handler)

        web.run_app(self.app, host=self._host, port=self._port, print=None)

    async def _http_handler(self, request: web.Request) -> web.Response:
        path = request.path
        method = request.method

        # Must be GET
        if method != "GET":
            return self._response_405_method_not_allowed()

        # Parse URL
        result = urllib.parse.urlparse(path)

        # Validate path
        path = result.path
        if ".." in path:
            return self._response_400_bad_request()

        # `/` -> `/index.html`
        if path == "/":
            path = "/index.html"

        # Remove initial `/`
        while path.startswith("/"):
            path = path[1:]

        # Respond with file
        return self._response_file(PATH_PUBLIC / path)

    async def _ws_handler(self, request: web.Request) -> web.StreamResponse:
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        self._logger.debug("WebSocket connect")
        self._ws_clients.add(ws)

        # Call `_ws_connect_callback`
        if self._ws_connect_callback is not None:
            for data in self._ws_connect_callback():
                await ws.send_str(data)

        # Call `ws_connect_message` for every message
        async for msg in ws:
            self._logger.debug(f"WebSocket message: {msg.data}")
            if msg.type == WSMsgType.TEXT:
                if self._ws_message_callback is not None:
                    for data in self._ws_message_callback(msg.data):
                        await ws.send_str(data)
            elif msg.type == WSMsgType.ERROR:
                self._logger.warning(f"WebSocket error: {ws.exception()}")

        self._logger.debug("WebSocket disconnected")
        self._ws_clients.remove(ws)

        return ws

    def ws_broadcast(self, data: str) -> None:
        asyncio.run(self.ws_broadcast_async(data))

    async def ws_broadcast_async(self, data: str) -> None:
        asyncio.gather(ws.send_str(data) for ws in self._ws_clients)

    def _response_400_bad_request(self) -> web.Response:
        return web.Response(status=400, text="400 Bad Request")

    def _response_403_forbidden(self) -> web.Response:
        return web.Response(status=403, text="403 Forbidden")

    def _response_404_not_found(self) -> web.Response:
        return web.Response(status=404, text="404 Not Found")

    def _response_405_method_not_allowed(self) -> web.Response:
        return web.Response(status=405, text="404 Method Not Allowed")

    def _response_file(self, path: Path) -> web.Response:
        # Check file existence
        if not path.is_file():
            self._logger.warning(f"Requested file '{path}' not found")
            return self._response_404_not_found()

        # Check mime type
        suffix = path.suffix.lower()
        if suffix not in ALLOWED_MIME_TYPES:
            return self._response_403_forbidden()
        mime_type = ALLOWED_MIME_TYPES[suffix]

        # Send file
        with path.open("rb") as file:
            return web.Response(status=200, content_type=mime_type, body=file.read())
