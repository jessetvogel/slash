import shutil
import urllib.parse
import weakref
from collections.abc import Awaitable, Mapping
from dataclasses import dataclass
from pathlib import Path
from ssl import SSLContext
from types import MappingProxyType
from typing import Callable

from aiohttp import BodyPartReader, WSCloseCode, WSMsgType, web

import slash
from slash._logging import LOGGER
from slash._utils import random_id

PATH_PUBLIC = Path(slash.__file__).resolve().parent / "public"
PATH_TMP = Path("./__slash_tmp__")

ALLOWED_MIME_TYPES = {
    ".html": "text/html",
    ".css": "text/css",
    ".js": "text/javascript",
    ".png": "image/png",
    ".ttf": "font/ttf",
    ".txt": "plain/txt",
}


@dataclass
class UploadedFile:
    """Class containing information about an uploaded file.

    Args:
        name: Name of the uploaded file.
        path: Path to the temporarily saved file.
        size: Size of the file in bytes.
    """

    name: str
    path: Path
    size: int


@dataclass
class UploadEvent:
    """Event that fires when one or more file are uploaded.

    Args:
        files: List of uploaded files.
    """

    files: list[UploadedFile]


class Client:
    def __init__(
        self,
        send: Callable[[str], Awaitable[None]],
        *,
        cookies: Mapping[str, str] | None = None,
    ):
        self._id = random_id()
        self._send = send
        self._cookies = dict(cookies or {})
        self._localstorage: dict[str, str] = {}

    @property
    def id(self) -> str:
        return self._id

    @property
    def cookies(self) -> Mapping[str, str]:
        return MappingProxyType(self._cookies)

    async def send(self, data: str) -> None:
        await self._send(data)

    def localstorage_set(self, key: str, value: str | None) -> None:
        if value is None:
            self._localstorage.pop(key, None)
        else:
            self._localstorage[key] = value

    def localstorage_get(self, key: str) -> str | None:
        return self._localstorage.get(key, None)


class Server:
    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 8080,
        *,
        ssl_context: SSLContext | None = None,
        enable_upload: bool = True,
        max_upload_size: int = 10_000_000,  # 10 MB
    ) -> None:
        self._host = host
        self._port = port
        self._ssl_context = ssl_context
        self._enable_upload = enable_upload
        self._max_upload_size = max_upload_size

        self._callback_ws_connect: Callable[[Client], Awaitable[None]] | None = None
        self._callback_ws_message: Callable[[Client, str], Awaitable[None]] | None = None
        self._callback_ws_disconnect: Callable[[Client], Awaitable[None]] | None = None

        self._files: dict[str, Path] = {}
        self._upload_callbacks: dict[str, Callable[[UploadEvent], None]] = {}

    def on_ws_connect(self, callback: Callable[[Client], Awaitable[None]]) -> None:
        self._callback_ws_connect = callback

    def on_ws_message(self, callback: Callable[[Client, str], Awaitable[None]]) -> None:
        self._callback_ws_message = callback

    def on_ws_disconnect(self, callback: Callable[[Client], Awaitable[None]]) -> None:
        self._callback_ws_disconnect = callback

    def serve(self) -> None:
        scheme = "https" if self._ssl_context is not None else "http"
        LOGGER.info(f"Serving on {scheme}://{self._host}:{self._port} .. (Press Ctrl+C to quit)")

        # Create web.Application
        self.app = web.Application()
        self.app.router.add_route("GET", "/ws", self._on_ws_request)
        self.app.router.add_route("POST", "/{tail:.*}", self._on_http_post_request)
        self.app.router.add_route("GET", "/{tail:.*}", self._on_http_get_request)

        # Keep track of websocket connections (to close on shutdown)
        self._websockets: weakref.WeakSet[web.WebSocketResponse] = weakref.WeakSet()
        self.app.on_shutdown.append(self._on_shutdown)

        # Run web app
        try:
            web.run_app(self.app, host=self._host, port=self._port, ssl_context=self._ssl_context, print=None)
        except Exception as err:
            LOGGER.error(str(err))

    async def _on_ws_request(self, request: web.Request) -> web.StreamResponse:
        # Construct websocket response
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        LOGGER.debug("WebSocket connect")

        # Create client instance to keep track of connection details
        client = Client(ws.send_str, cookies=request.cookies)

        # Keep track of websocket connection
        self._websockets.add(ws)

        try:
            # Call `_callback_ws_connect`
            if self._callback_ws_connect is not None:
                await self._callback_ws_connect(client)

            # Call `_callback_ws_message` for every message
            async for msg in ws:
                LOGGER.debug(f"WebSocket message: {msg.data}")
                if msg.type == WSMsgType.TEXT:
                    if self._callback_ws_message is not None:
                        await self._callback_ws_message(client, msg.data)
                elif msg.type == WSMsgType.ERROR:
                    LOGGER.warning(f"WebSocket error: {ws.exception()}")

            LOGGER.debug("WebSocket disconnect")

            # Call `_callback_ws_disconnect`
            if self._callback_ws_disconnect is not None:
                await self._callback_ws_disconnect(client)
        finally:
            self._websockets.discard(ws)

        return ws

    async def _on_http_get_request(self, request: web.Request) -> web.Response:
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

        # Check if path in `self._files`
        if path in self._files:
            return self._response_file(self._files[path])

        # Asset files
        if (
            path.startswith("/css/")
            or path.startswith("/fonts/")
            or path.startswith("/img/")
            or path.startswith("/js/")
        ):
            return self._response_file(PATH_PUBLIC / path[1:])

        # Otherwise, return `index.html`
        return self._response_file(PATH_PUBLIC / "index.html")

    async def _on_http_post_request(self, request: web.Request) -> web.Response:
        path = request.path
        method = request.method

        # Method must be POST
        if method != "POST":
            return self._response_405_method_not_allowed()

        # Check if file upload is enabled
        if not self._enable_upload:
            return self._response_403_forbidden("file upload is disabled")

        # Check if path corresponds to an upload callback
        if path in self._upload_callbacks:
            callback = self._upload_callbacks[path]

            # Expect 'Content-Type: multipart/form-data'
            if not request.content_type.startswith("multipart/form-data"):
                self._response_400_bad_request("expected content type multipart/form-data")

            # Create temporary directory if non-existent
            PATH_TMP.mkdir(exist_ok=True)

            # Write files to temporary directory
            reader = await request.multipart()
            files: list[UploadedFile] = []
            while (field := await reader.next()) is not None:
                if isinstance(field, BodyPartReader) and field.filename:
                    name = field.filename
                    extension = Path(name).suffix.lower()
                    size = 0
                    # Use random filename for safety and to not overwrite any files
                    filepath = PATH_TMP / (random_id() + extension)
                    with filepath.open("wb") as file:
                        while chunk := await field.read_chunk():
                            file.write(chunk)
                            size += len(chunk)
                            if size >= self._max_upload_size:
                                return self._response_413_content_too_large(
                                    f"maximum file size is {self._max_upload_size} bytes"
                                )
                    files.append(UploadedFile(name, filepath, size))

            # If no files were uploaded, respond with bad request
            if not files:
                return self._response_400_bad_request("no files were uploaded")

            # Call callback
            try:
                callback(UploadEvent(files))
            except Exception as err:
                LOGGER.error(f"Error occurred during handling upload event: {err}")

            return web.Response(status=200, text=f"{len(files)} files uploaded")

        LOGGER.warning(f"Unexpected POST request to '{path}'")
        return self._response_404_not_found()

    async def _on_shutdown(self, _: web.Application) -> None:
        LOGGER.info("Server shutdown")
        # Close all open websocket connections
        for ws in set(self._websockets):
            await ws.close(code=WSCloseCode.GOING_AWAY, message=b"server shutdown")
        # Remove temporary directory (if exists)
        if PATH_TMP.exists() and PATH_TMP.is_dir():
            shutil.rmtree(PATH_TMP)

    def _response_400_bad_request(self, msg: str | None = None) -> web.Response:
        text = f"400 Bad Request ({msg})" if msg else "400 Bad Request"
        return web.Response(status=400, text=text)

    def _response_403_forbidden(self, msg: str | None = None) -> web.Response:
        text = f"403 Forbidden ({msg})" if msg else "403 Forbidden"
        return web.Response(status=403, text=text)

    def _response_404_not_found(self) -> web.Response:
        return web.Response(status=404, text="404 Not Found")

    def _response_405_method_not_allowed(self) -> web.Response:
        return web.Response(status=405, text="405 Method Not Allowed")

    def _response_413_content_too_large(self, msg: str | None = None) -> web.Response:
        text = f"413 Content Too Large ({msg})" if msg else "413 Content Too Large"
        return web.Response(status=413, text=text)

    def _response_file(self, path: Path, *, status: int = 200) -> web.Response:
        # Check file existence
        if not path.is_file():
            LOGGER.warning(f"Requested file '{path}' not found")
            return self._response_404_not_found()

        # Check mime type
        suffix = path.suffix.lower()
        if suffix not in ALLOWED_MIME_TYPES:
            return self._response_403_forbidden()
        mime_type = ALLOWED_MIME_TYPES[suffix]

        # Send file
        with path.open("rb") as file:
            return web.Response(status=status, content_type=mime_type, body=file.read())

    def share_file(self, url: str, path: Path) -> None:
        self._files[url] = path

    def accept_file(self, url: str, callback: Callable[[UploadEvent], None]) -> None:
        if not self._enable_upload:
            raise RuntimeError(
                "File uploading is disabled. To enable file uploading, set `enable_upload` to `True` in `App`."
            )
        self._upload_callbacks[url] = callback
