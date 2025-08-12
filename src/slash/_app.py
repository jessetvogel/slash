from __future__ import annotations

import re
import traceback
from collections.abc import Callable
from ssl import SSLContext

import markdown

from slash._logging import LOGGER
from slash._message import Message
from slash._pages import page_404
from slash._server import Client, Server
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


class App:
    """Main class for a Slash web application.

    Args:
        host: Hostname on which to serve the web server.
        port: Port on which to serve the web server.
        ssl_context: SSL context to use for the web server.
        enable_upload: Boolean flag indicating whether file upload is enabled.
        max_upload_size: Maximum file size for uploaded files in bytes.
    """

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 8080,
        *,
        ssl_context: SSLContext | None = None,
        enable_upload: bool = True,
        max_upload_size: int = 10_000_000,  # 10 MB
    ) -> None:
        self._server = Server(
            host, port, ssl_context=ssl_context, enable_upload=enable_upload, max_upload_size=max_upload_size
        )
        self._routes: dict[str | re.Pattern, Callable[..., Elem]] = {}
        self._sessions: dict[str, Session] = {}

    def add_route(self, pattern: str, root: Callable[..., Elem]) -> None:
        """Add route from a path pattern.

        Args:
            pattern: String or regex pattern to match the path of the URL.
            root: Function that returns the root element of the page.
                If `pattern` is a :py:class:`re.Pattern`, the matched groups will
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

    def run(self) -> None:
        """Run the application."""
        self._server.on_ws_connect(self._handle_ws_connect)
        self._server.on_ws_message(self._handle_ws_message)
        self._server.on_ws_disconnect(self._handle_ws_disconnect)
        self._server.serve()

    async def _handle_ws_connect(self, client: Client) -> None:
        # Create and store new session instance for client
        session = Session(self._server, client)
        self._sessions[client.id] = session

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
                error = traceback.format_exc()
                error_mk = "\n".join(["    " + line for line in error.split("\n")])
                msg = markdown.markdown(error_mk)
                session.log("error", f"<b>Server error</b>{markdown.markdown(msg)}", format="html")
            await session.flush()

    async def _handle_ws_disconnect(self, client: Client) -> None:
        # Forget session corresponding to client
        self._sessions.pop(client.id)

    def _handle_load_message(self, message: Message) -> None:
        """Handle load event."""
        session = Session.require()
        url = message.data["url"]
        if not isinstance(url, str):
            msg = f"Error in `load` event: expected `url` of type string, but got `{type(url).__name__}`."
            raise BadMessageException(msg)
        try:
            session._location = Location(url)  # NOTE: not very clean, but effective
        except Exception as err:
            msg = f"Error in `load` event: invalid `url` (`{url}`)."
            raise BadMessageException(msg) from err

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
