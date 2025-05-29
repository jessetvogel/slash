from __future__ import annotations

from collections.abc import Callable
import random
import time
from slash.core import Elem, Page, MouseEvent
from slash.message import Message
from slash.server import Server


class App:
    def __init__(self):
        self.server = Server("127.0.0.1", 8080)
        self.pages: dict[str, Page] = {}

    def add_endpoint(self, endpoint: str, root: Callable[[], Elem]):
        self.pages[endpoint] = Page(root)

    def run(self):
        self.server.on_ws_connect(self._on_ws_connect)
        self.server.on_ws_message(self._on_ws_message)
        self.server.serve()

    def _on_ws_connect(self) -> list[str]:
        page = self.pages["/"]
        return [message.to_json() for message in page.root.build()]

    def _on_ws_message(self, data: str) -> list[str]:
        page = self.pages["/"]
        message = Message.from_json(data)

        # click
        if message.event == "click":
            id = message.data["id"]
            elem = page.find(id)
            if elem is None:
                print(f"Clicked on invalid id '{id}'")
            else:
                elem.click(MouseEvent(elem))

        return [message.to_json() for message in page.poop()]
