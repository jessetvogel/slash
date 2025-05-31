from __future__ import annotations

from collections.abc import Callable
from slash.core import (
    ChangeEvent,
    Elem,
    InputEvent,
    Page,
    ClickEvent,
    SupportsOnChange,
    SupportsOnClick,
    SupportsOnInput,
)
from slash.message import Message
from slash.server import Server


class App:
    def __init__(self) -> None:
        self.server = Server("127.0.0.1", 8080)
        self.pages: dict[str, Page] = {}

    def add_endpoint(self, endpoint: str, root: Callable[[], Elem]) -> None:
        self.pages[endpoint] = Page(root)

    def run(self) -> None:
        self.server.on_ws_connect(self._handle_ws_connect)
        self.server.on_ws_message(self._handle_ws_message)
        self.server.serve()

    def _handle_ws_connect(self) -> list[str]:
        page = self.pages["/"]
        return [message.to_json() for message in page.root.build()]

    def _handle_ws_message(self, data: str) -> list[str]:
        page = self.pages["/"]
        message = Message.from_json(data)

        # click
        if message.event == "click":
            id = message.data["id"]
            elem = page.find(id)
            if not isinstance(elem, SupportsOnClick):
                page.broadcast(
                    Message.log("error", f"Element '{id}' does not support click")
                )
            else:
                elem.click(ClickEvent(elem))

        # input
        if message.event == "input":
            id = message.data["id"]
            elem = page.find(id)
            if not isinstance(elem, SupportsOnInput):
                page.broadcast(
                    Message.log("error", f"Element '{id}' does not support input")
                )
            else:
                elem.input(InputEvent(elem, message.data["value"]))

        # change
        if message.event == "change":
            id = message.data["id"]
            elem = page.find(id)
            if not isinstance(elem, SupportsOnChange):
                page.broadcast(
                    Message.log("error", f"Element '{id}' does not support change")
                )
            else:
                elem.change(ChangeEvent(elem, message.data["value"]))

        return [message.to_json() for message in page.poop()]
