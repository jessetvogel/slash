from __future__ import annotations

from collections.abc import Callable
from slash.client import Client
from slash.core import (
    ChangeEvent,
    Elem,
    InputEvent,
    Context,
    ClickEvent,
    SupportsOnChange,
    SupportsOnClick,
    SupportsOnInput,
)
from slash.logging import create_logger
from slash.message import Message
from slash.server import Server

import traceback


class App:
    def __init__(self) -> None:
        self._server = Server("127.0.0.1", 8080)
        self._endpoints: dict[str, Elem] = {}
        self._clients: dict[int, Client] = {}
        self._context = Context()
        self._logger = create_logger()

    def add_endpoint(self, endpoint: str, root: Callable[[], Elem]) -> None:
        elem = root()
        elem.set_context(self._context)
        self._endpoints[endpoint] = elem

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
        root = self._endpoints["/"]

        client = self._get_client(client_id)
        self._context.client = client  # set client
        try:
            root.mount()
        except Exception as err:
            client.flush()
            msg = "Server error: " + str(err)
            self._logger.error(msg)
            client.log("error", msg)
        self._context.client = None  # unset client

        return self._respond_client(client)

    def _handle_ws_message(self, client_id: int, data: str) -> list[str]:
        client = self._get_client(client_id)

        self._context.client = client  # set client
        try:
            message = Message.from_json(data)

            # click
            if message.event == "click":
                id = message.data["id"]
                elem = self._context.get_elem(id)
                if not isinstance(elem, SupportsOnClick):
                    client.log("error", f"element '{id}' does not support click")
                else:
                    elem.click(ClickEvent(elem))

            # input
            elif message.event == "input":
                id = message.data["id"]
                elem = self._context.get_elem(id)
                if not isinstance(elem, SupportsOnInput):
                    client.log("error", f"element '{id}' does not support input")
                else:
                    elem.input(InputEvent(elem, message.data["value"]))

            # change
            elif message.event == "change":
                id = message.data["id"]
                elem = self._context.get_elem(id)
                if not isinstance(elem, SupportsOnChange):
                    client.log("error", f"element '{id}' does not support change")
                else:
                    elem.change(ChangeEvent(elem, message.data["value"]))

        except Exception:
            client.flush()
            client.send(self._message_server_error(traceback.format_exc()))

        self._context.client = None  # unset client

        return self._respond_client(client)

    def _handle_ws_disconnect(self, client_id: int) -> None:
        self._remove_client(client_id)

    def _respond_client(self, client: Client) -> list[str]:
        try:
            # Host files
            for url, path in client.flush_files().items():
                self._server.host(url, path)

            # Serialize messages
            messages = [message.to_json() for message in client.flush()]
        except Exception:
            return [self._message_server_error(traceback.format_exc()).to_json()]

        return messages

    def _message_server_error(self, error: str) -> Message:
        return Message.log(
            "error",
            f"<span>Unexpected server error.</span><pre>{error}</pre>",
        )
