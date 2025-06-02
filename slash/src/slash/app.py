from __future__ import annotations

from collections.abc import Callable
from slash.client import Client
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
from slash.logging import create_logger
from slash.message import Message
from slash.server import Server


class App:
    def __init__(self) -> None:
        self._server = Server("127.0.0.1", 8080)
        self._pages: dict[str, Page] = {}
        self._clients: dict[int, Client] = {}
        self._logger = create_logger()

    def add_endpoint(self, endpoint: str, root: Callable[[], Elem]) -> None:
        self._pages[endpoint] = Page(root)

    def run(self) -> None:
        self._server.on_ws_connect(self._handle_ws_connect)
        self._server.on_ws_message(self._handle_ws_message)
        self._server.on_ws_disconnect(self._handle_ws_disconnect)
        self._server.serve()

    def _get_client(self, client_id: int) -> Client:
        if client_id not in self._clients:
            self._clients[client_id] = Client()
        return self._clients[client_id]

    def _remove_client(self, client_id: int) -> None:
        self._clients.pop(client_id)

    def _handle_ws_connect(self, client_id: int) -> list[str]:
        client = self._get_client(client_id)

        page = self._pages["/"]
        page.client = client

        try:
            messages = self._build_and_mount_all(page.root)
            messages.extend(client.flush())
            return [message.to_json() for message in messages]
        except Exception as err:
            msg = "Server error: " + str(err)
            self._logger.error(msg)
            return [Message.log("error", msg).to_json()]

    def _handle_ws_message(self, client_id: int, data: str) -> list[str]:
        client = self._get_client(client_id)

        page = self._pages["/"]

        try:
            message = Message.from_json(data)

            # click
            if message.event == "click":
                id = message.data["id"]
                elem = page.find(id)
                if not isinstance(elem, SupportsOnClick):
                    client.log("error", f"element '{id}' does not support click")
                else:
                    elem.click(ClickEvent(elem))

            # input
            if message.event == "input":
                id = message.data["id"]
                elem = page.find(id)
                if not isinstance(elem, SupportsOnInput):
                    client.log("error", f"element '{id}' does not support input")
                else:
                    elem.input(InputEvent(elem, message.data["value"]))

            # change
            if message.event == "change":
                id = message.data["id"]
                elem = page.find(id)
                if not isinstance(elem, SupportsOnChange):
                    client.log("error", f"element '{id}' does not support change")
                else:
                    elem.change(ChangeEvent(elem, message.data["value"]))

            return [message.to_json() for message in client.flush()]
        except Exception as err:
            return [Message.log("error", str(err)).to_json()]

    def _handle_ws_disconnect(self, client_id: int) -> None:
        self._remove_client(client_id)

    def _build_and_mount_all(self, elem: Elem) -> list[Message]:
        elem.mount()
        messages = [elem.create()]
        for child in elem.children:
            if isinstance(child, Elem):
                messages.extend(self._build_and_mount_all(child))
            else:
                messages.append(
                    Message(event="create", tag="text", parent=elem.id, text=child)
                )
        return messages
