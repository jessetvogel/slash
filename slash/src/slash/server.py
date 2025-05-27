import logging
from pathlib import Path
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
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

        # Set custom logger
        self.logger = slash.logging.create_logger()

        # Other
        self.ws_clients: set[web.WebSocketResponse] = set()

    def serve(self):
        self.logger.info(f"Serving on {self.host}:{self.port} ..")

        self.app = web.Application()
        self.app.router.add_get("/ws", self._ws_handler)
        self.app.router.add_route("*", "/{tail:.*}", self._http_handler)

        web.run_app(self.app, host=self.host, port=self.port)

    async def _http_handler(self, request: web.Request) -> web.Response:
        path = request.path
        method = request.method

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

        self.logger.debug("New WS client")
        self.ws_clients.add(ws)

        async for msg in ws:
            self.logger.debug(f"Incoming WS message: {msg.data}")
            if msg.type == WSMsgType.TEXT:
                await ws.send_str(f"Echo: {msg.data}")
            elif msg.type == WSMsgType.ERROR:
                print(f"WebSocket error: {ws.exception()}")

        self.logger.debug("WS client disconnected")
        self.ws_clients.remove(ws)

        return ws

    async def ws_broadcast(self, data: str) -> None:
        for ws in self.ws_clients:
            await ws.send_str(data)

    def _response_400_bad_request(self) -> web.Response:
        return web.Response(status=400, text="400 Bad Request")

    def _response_403_forbidden(self) -> web.Response:
        return web.Response(status=403, text="403 Forbidden")

    def _response_404_not_found(self) -> web.Response:
        return web.Response(status=404, text="404 Not Found")

    def _response_file(self, path: Path) -> web.Response:
        # Check file existence
        if not path.is_file():
            print(f"{path} not found")
            return self._response_404_not_found()

        # Check mime type
        suffix = path.suffix.lower()
        if suffix not in ALLOWED_MIME_TYPES:
            return self._response_403_forbidden()
        mime_type = ALLOWED_MIME_TYPES[suffix]

        # Send file
        with path.open("rb") as file:
            return web.Response(status=200, content_type=mime_type, body=file.read())
