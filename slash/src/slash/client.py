from pathlib import Path
from typing import Any
from slash.js import JSFunction
from slash.logging import get_logger
from slash.message import Message
from slash.server import Server, WSClient
from slash.utils import random_id

LOGGER = get_logger()


class Client:
    def __init__(self, ws_client: WSClient, server: Server) -> None:
        self._ws_client = ws_client
        self._server = server
        self._queue: list[str] = []
        self._files: dict[str, Path] = {}
        self._mounted_elems: set[str] = set()  # elements that client already has
        self._functions: set[str] = set()  # functions that client already has

    def send(self, message: Message) -> None:
        try:
            self._queue.append(message.to_json())
        except TypeError as err:
            LOGGER.error(f"Failed to serialize message: {err}")

    def log(self, type: str, message: str) -> None:
        self.send(Message.log(type, message))

    def execute(
        self, jsfunction: JSFunction, args: list[Any], store: str | None = None
    ) -> None:
        # Define function if not defined yet
        if jsfunction.id not in self._functions:
            self.send(Message.function(jsfunction.id, jsfunction.args, jsfunction.body))
            self._functions.add(jsfunction.id)
        # Execute function with given arguments
        self.send(Message.execute(jsfunction.id, args, store))

    async def flush(self) -> None:
        # Host all files and reset
        for url, path in self._files.items():
            self._server.host(url, path)
        self._files = {}

        # Send all messages and reset queue
        for data in self._queue:
            await self._ws_client.send(data)
        self._queue = []

    def host(self, path: Path) -> str:
        """Returns URL at which the resource can be accessed."""
        url = f"/tmp/{random_id()}"
        self._files[url] = path
        return url
