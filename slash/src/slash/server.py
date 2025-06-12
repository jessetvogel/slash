import asyncio
from pathlib import Path
from typing import Callable
import urllib.parse
import weakref

import slash.logging

from aiohttp import WSCloseCode, WSMsgType, web
from slash.utils import random_id

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

        self._callback_ws_connect: (
            Callable[[str, Callable[[str], None]], None] | None
        ) = None
        self._callback_ws_message: Callable[[str, str], None] | None = None
        self._callback_ws_disconnect: Callable[[str], None] | None = None

        self._files: dict[str, Path] = {}

    def on_ws_connect(
        self, callback: Callable[[str, Callable[[str], None]], None]
    ) -> None:
        self._callback_ws_connect = callback

    def on_ws_message(self, callback: Callable[[str, str], None]) -> None:
        self._callback_ws_message = callback

    def on_ws_disconnect(self, callback: Callable[[str], None]) -> None:
        self._callback_ws_disconnect = callback

    def serve(self) -> None:
        self._logger.info(
            f"Serving on http://{self._host}:{self._port} .. (Press Ctrl+C to quit)"
        )

        # Create web.Application
        self.app = web.Application()
        self.app.router.add_get("/ws", self._on_ws_request)
        self.app.router.add_route("*", "/{tail:.*}", self._on_http_request)

        # Keep track of websocket connections (to close on shutdown)
        self._websockets: weakref.WeakSet[web.WebSocketResponse] = weakref.WeakSet()
        self.app.on_shutdown.append(self._on_shutdown)

        # Run web app
        web.run_app(self.app, host=self._host, port=self._port, print=None)

    async def _on_shutdown(self, _: web.Application) -> None:
        self._logger.info("Server shutdown")
        for ws in set(self._websockets):
            await ws.close(code=WSCloseCode.GOING_AWAY, message=b"server shutdown")

    async def _on_http_request(self, request: web.Request) -> web.Response:
        path = request.path
        method = request.method

        # Method must be GET
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

        # Check if path in `self._files`
        if path in self._files:
            return self._response_file(self._files[path])

        # Remove initial `/`
        while path.startswith("/"):
            path = path[1:]

        # Respond with file
        return self._response_file(PATH_PUBLIC / path)

    async def _on_ws_request(self, request: web.Request) -> web.StreamResponse:
        # Construct websocket response
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        self._logger.debug("WebSocket connect")

        # Callback function to send messages over websocket
        def responder(data: str) -> None:
            asyncio.create_task(ws.send_str(data))

        # Keep track of websocket connection
        self._websockets.add(ws)

        try:
            client_id = random_id()

            # Call `_callback_ws_connect`
            if self._callback_ws_connect is not None:
                self._callback_ws_connect(client_id, responder)

            # Call `_callback_ws_message` for every message
            async for msg in ws:
                self._logger.debug(f"WebSocket message: {msg.data}")
                if msg.type == WSMsgType.TEXT:
                    if self._callback_ws_message is not None:
                        self._callback_ws_message(client_id, msg.data)
                elif msg.type == WSMsgType.ERROR:
                    self._logger.warning(f"WebSocket error: {ws.exception()}")

            self._logger.debug("WebSocket disconnected")

            # Call `_callback_ws_disconnect`
            if self._callback_ws_disconnect is not None:
                self._callback_ws_disconnect(client_id)
        finally:
            self._websockets.discard(ws)

        return ws

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

    def host(self, url: str, path: Path) -> None:
        self._files[url] = path
