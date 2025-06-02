from typing import Any
from slash.jsfunction import JSFunction
from slash.message import Message


class Client:
    def __init__(self) -> None:
        self._queue: list[Message] = []
        self._functions: set[str] = set()  # received function ids

    def log(self, type: str, message: str) -> None:
        self._queue.append(Message.log(type, message))

    def execute(
        self, jsfunction: JSFunction, args: list[Any], store: str | None = None
    ) -> None:
        # Define function if not defined yet
        if jsfunction.id not in self._functions:
            self._queue.append(
                Message.function(jsfunction.id, jsfunction.args, jsfunction.body)
            )
            self._functions.add(jsfunction.id)
        # Execute function with given arguments
        self._queue.append(Message.execute(jsfunction.id, args, store))

    def flush(self) -> list[Message]:
        queue = self._queue
        self._queue = []
        return queue

    def reply(self, message: Message) -> None:
        self._queue.append(message)
