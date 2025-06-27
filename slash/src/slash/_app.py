"""Slash app."""

from __future__ import annotations

import traceback
from collections.abc import Callable

from slash._logging import LOGGER
from slash._message import Message
from slash._server import Client, Server
from slash.core import Elem, Session
from slash.events import (
    ChangeEvent,
    ClickEvent,
    InputEvent,
    SupportsOnChange,
    SupportsOnClick,
    SupportsOnInput,
)


class App:
    def __init__(self) -> None:
        self._server = Server("127.0.0.1", 8080)
        self._endpoints: dict[str, Callable[[], Elem]] = {}
        self._sessions: dict[str, Session] = {}

    def add_endpoint(self, endpoint: str, root: Callable[[], Elem]) -> None:
        self._endpoints[endpoint] = root

    def run(self) -> None:
        self._server.on_ws_connect(self._handle_ws_connect)
        self._server.on_ws_message(self._handle_ws_message)
        self._server.on_ws_disconnect(self._handle_ws_disconnect)
        self._server.serve()

    async def _handle_ws_connect(self, client: Client) -> None:
        # Create new session
        self._sessions[client.id] = (session := Session(self._server, client))

        with session:
            try:
                # Create and mount root element
                root = self._endpoints["/"]()
                root.mount()
            except Exception as err:
                msg = "Server error: " + str(err)
                LOGGER.error(msg)
                session.log("error", msg)
            await session.flush()

    async def _handle_ws_message(self, client: Client, data: str) -> None:
        if client.id not in self._sessions:
            LOGGER.error(f"Unknown client id {client.id}")
            return

        session = self._sessions[client.id]

        with session:
            try:
                message = Message.from_json(data)

                # click
                if message.event == "click":
                    id = message.data["id"]
                    elem = session.get_elem(id)
                    if not isinstance(elem, SupportsOnClick):
                        session.log("error", f"element '{id}' does not support click")
                    else:
                        elem.click(ClickEvent(elem))

                # input
                elif message.event == "input":
                    id = message.data["id"]
                    elem = session.get_elem(id)
                    if not isinstance(elem, SupportsOnInput):
                        session.log("error", f"element '{id}' does not support input")
                    else:
                        elem.input(InputEvent(elem, message.data["value"]))

                # change
                elif message.event == "change":
                    id = message.data["id"]
                    elem = session.get_elem(id)
                    if not isinstance(elem, SupportsOnChange):
                        session.log("error", f"element '{id}' does not support change")
                    else:
                        elem.change(ChangeEvent(elem, message.data["value"]))

            except Exception:
                session.send(self._message_server_error(traceback.format_exc()))

            await session.flush()

    async def _handle_ws_disconnect(self, client: Client) -> None:
        self._sessions.pop(client.id)

    # def _respond_client(self, client: Client) -> list[str]:
    #     try:
    #         # Host files
    #         for url, path in client.flush_files().items():
    #             self._server.host(url, path)

    #         # Serialize messages
    #         messages = [message.to_json() for message in client.flush()]
    #     except Exception:
    #         return [self._message_server_error(traceback.format_exc()).to_json()]

    #     return messages

    def _message_server_error(self, error: str) -> Message:
        return Message.log(
            "error",
            f"<span>Unexpected server error.</span><pre><code>{error}</code></pre>",
        )
