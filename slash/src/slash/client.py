from pathlib import Path
from typing import Any
from slash.jsfunction import JSFunction
from slash.message import Message
from slash.utils import random_id


class Client:
    def __init__(self) -> None:
        self._queue: list[Message] = []
        self._files: dict[str, Path] = {}
        self._elems: set[str] = set()  # elements that client already has
        self._functions: set[str] = set()  # functions that client already has

    def send(self, message: Message) -> None:
        self._queue.append(message)

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

    def flush(self) -> list[Message]:
        queue = self._queue
        self._queue = []
        return queue

    def flush_files(self) -> dict[str, Path]:
        files = self._files
        self._files = {}
        return files

    def host(self, path: Path) -> str:
        """Returns URL at which the resource can be accessed."""
        url = f"/tmp/{random_id()}"
        self._files[url] = path
        return url
