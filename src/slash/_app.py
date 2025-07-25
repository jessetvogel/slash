"""Slash app."""

from __future__ import annotations

import re
import traceback
from collections.abc import Callable
from pathlib import Path
from ssl import SSLContext

import markdown

from slash._config import Config
from slash._logging import LOGGER
from slash._message import Message
from slash._pages import page_404
from slash._server import Client, Server
from slash._utils import random_id
from slash.core import Elem, Location, PopStateEvent, Session
from slash.events import (
    ChangeEvent,
    ClickEvent,
    InputEvent,
    SupportsOnChange,
    SupportsOnClick,
    SupportsOnInput,
)


class BadMessageException(Exception):
    pass


class Router:
    def __init__(self) -> None:
        self._routes: dict[str | re.Pattern, Callable[..., Elem]] = {}

    def add_route(self, pattern: str, root: Callable[..., Elem]) -> None:
        """Add route.

        Args:
            pattern: Pattern to match the path of the URL.
                Can be either string or regex pattern.
            root: Function that returns a root element of the page.
                If pattern is a `re.Pattern`, the matched groups will
                be provided to the function as arguments.
        """
        is_regex = any(c in pattern for c in ".^$*+?{}[]\\|()")
        self._routes[re.compile(f"^{pattern}$") if is_regex else pattern] = root

    def _create_root(self) -> Elem:
        """Create a root element from the current client state."""
        session = Session.require()
        for pattern, root in self._routes.items():
            if isinstance(pattern, str) and pattern == session.location.path:
                return root()
            if isinstance(pattern, re.Pattern):
                if (m := pattern.match(session.location.path)) is not None:
                    return root(*m.groups())
        return page_404()


class App(Router):
    """Main class for a Slash web application."""

    def __init__(self) -> None:
        Router.__init__(self)
        self._config = Config()
        self._server = Server(self.config.host, self.config.port)
        self._sessions: dict[str, Session] = {}
        self._stylesheets: list[str] = []

    @property
    def config(self) -> Config:
        """Configuration object of application."""
        return self._config

    def add_stylesheet(self, path: Path) -> None:
        """Add stylesheet.

        Args:
            path: Path to stylesheet.
        """
        url = f"/style/{random_id()}.css"
        self._server.add_file(url, path)
        self._stylesheets.append(url)

    def set_ssl_context(self, ssl_context: SSLContext) -> None:
        self._server.set_ssl_context(ssl_context)

    def run(self) -> None:
        """Start application."""
        self._server.host = self.config.host
        self._server.port = self.config.port
        self._server.on_ws_connect(self._handle_ws_connect)
        self._server.on_ws_message(self._handle_ws_message)
        self._server.on_ws_disconnect(self._handle_ws_disconnect)
        self._server.serve()

    def _send_stylesheets(self) -> None:
        """Send all stylesheets to the current client."""
        session = Session.require()
        for url in self._stylesheets:
            session.send(
                Message.create(
                    tag="link",
                    id=random_id(),
                    parent="head",
                    rel="stylesheet",
                    type="text/css",
                    href=url,
                )
            )

    async def _handle_ws_connect(self, client: Client) -> None:
        # Create and store new session instance for client
        session = Session(self._server, client)
        self._sessions[client.id] = session

        with session:
            # Send stylesheets
            self._send_stylesheets()
            await session.flush()

    async def _handle_ws_message(self, client: Client, data: str) -> None:
        # Get session corresponding to client id
        if client.id not in self._sessions:
            LOGGER.error(f"Unknown client id {client.id}")
            return

        with (session := self._sessions[client.id]):
            try:
                # Parse message
                message = Message.from_json(data)
                # `load` event
                if message.event == "load":
                    self._handle_load_message(message)
                # `click` event
                elif message.event == "click":
                    self._handle_click_message(message)
                # `input` event
                elif message.event == "input":
                    self._handle_input_message(message)
                # `change` event
                elif message.event == "change":
                    self._handle_change_message(message)
                # `popstate` event
                elif message.event == "popstate":
                    self._handle_popstate_message(message)
            except BadMessageException as err:
                session.log(
                    "error",
                    f"<b>Bad request</b>{markdown.markdown(str(err))}",
                    format="html",
                )
            except Exception:
                session.send(self._create_message_server_error(traceback.format_exc()))

            await session.flush()

    async def _handle_ws_disconnect(self, client: Client) -> None:
        # Forget session corresponding to client
        self._sessions.pop(client.id)

    def _create_message_server_error(self, error: str) -> Message:
        return Message.log(
            "error",
            f"<b>Unexpected server error</b><pre><code>{error}</code></pre>",
            format="html",
        )

    def _handle_load_message(self, message: Message) -> None:
        """Handle load event."""
        session = Session.require()
        url = message.data["url"]
        if not isinstance(url, str):
            msg = f"Error in `load` event: expected `url` of type string, but got `{type(url).__name__}`."
            raise BadMessageException(msg)
        try:
            session._location = Location(url)  # NOTE: not very clean, but effective
        except Exception:
            msg = f"Error in `load` event: invalid `url` (`{url}`)."
            raise BadMessageException(msg)

        Session.require().set_root(self._create_root())

    def _handle_click_message(self, message: Message) -> None:
        """Handle click event."""
        id = message.data["id"]
        elem = Session.require().get_elem(id)
        if not isinstance(elem, SupportsOnClick):
            msg = f"Error in `click` event: element '{id}' does not support click."
            raise BadMessageException(msg)
        elem.click(ClickEvent(elem))

    def _handle_input_message(self, message: Message) -> None:
        """Handle input event."""
        id = message.data["id"]
        elem = Session.require().get_elem(id)
        if not isinstance(elem, SupportsOnInput):
            msg = f"Error in `input` event: element '{id}' does not support input."
            raise BadMessageException(msg)
        elem.input(InputEvent(elem, message.data["value"]))

    def _handle_change_message(self, message: Message) -> None:
        """Handle change event."""
        id = message.data["id"]
        elem = Session.require().get_elem(id)
        if not isinstance(elem, SupportsOnChange):
            msg = f"Error in `change` event: element '{id}' does not support change."
            raise BadMessageException(msg)
        elem.change(ChangeEvent(elem, message.data["value"]))

    def _handle_popstate_message(self, message: Message) -> None:
        """Handle popstate event."""
        state = message.data["state"]
        Session.require().history.popstate(PopStateEvent(state=state))
