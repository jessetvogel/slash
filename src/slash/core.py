"""Slash core."""

from __future__ import annotations

import asyncio
import inspect
from collections.abc import Awaitable, Callable
from contextvars import ContextVar
from pathlib import Path
from typing import Any, Literal, Self, TypeAlias, TypeVar

from slash._logging import LOGGER
from slash._message import Message
from slash._server import Client, Server, UploadEvent
from slash._utils import random_id
from slash.js import JSFunction

# Types

T = TypeVar("T")

Handler: TypeAlias = (
    Callable[[T], Awaitable[None] | None] | Callable[[], Awaitable[None] | None]
)

# Session


class Session:
    """The `Session` class is used to communicate with the currently-connected user."""

    _current: ContextVar[Session] = ContextVar("session")

    def __init__(self, server: Server, client: Client) -> None:
        """Initialize session instance.

        Args:
            server: Server object.
            client: Client object.
        """
        self._server = server
        self._client = client

        self._queue_messages: list[str] = []
        self._queue_files: list[tuple[str, Path]] = []
        self._queue_upload_callbacks: list[
            tuple[str, Callable[[UploadEvent], None]]
        ] = []

        self._mounted_elems: dict[str, Elem] = {}  # elements that client already has
        self._functions: set[str] = set()  # functions that client already has

    @staticmethod
    def current() -> Session | None:
        """Get the current session."""
        try:
            return Session._current.get()
        except LookupError:
            pass
        return None

    @staticmethod
    def require() -> Session:
        """Get the current session. Raises an error if there is no current session."""
        try:
            return Session._current.get()
        except LookupError as err:
            raise RuntimeError("Session required, but no session was set") from err

    @property
    def id(self) -> str:
        """Get the id of the current session."""
        if not hasattr(self, "_id"):
            # Try to get session id from cookies
            id = self._client.cookies.get("SLASH_SESSION", None)
            if (
                id is None  # if `id` is not set in cookie
                or not id.startswith("_")  # or `id` has invalid format
                or not id[1:].isalnum()
                or len(id) != 7
            ):
                id = random_id()
                self.send(
                    Message(event="cookie", name="SLASH_SESSION", value=id, days=1)
                )
            self._id = id
        return self._id

    def add_elem(self, elem: Elem) -> None:
        """Mark element as mounted.

        Args:
            elem: Element to mark.
        """
        self._mounted_elems[elem.id] = elem

    def remove_elem(self, elem: Elem) -> None:
        """Unmark element as mounted.

        Args:
            elem: Element to unmark.
        """
        if elem.id in self._mounted_elems:
            self._mounted_elems.pop(elem.id)

    def get_elem(self, id: str) -> Elem | None:
        """Get element by id.

        Args:
            id: Id of element.

        Returns:
            Element with given id, or `None`.
        """
        return self._mounted_elems.get(id, None)

    def send(self, message: Message) -> None:
        """Send a message to the client.

        Args:
            message: Message to be sent.
        """
        try:
            self._queue_messages.append(message.to_json())
        except TypeError as err:
            LOGGER.error(f"Failed to serialize message: {err}")

    def log(
        self, type: Literal["info", "debug", "warning", "error"], message: str
    ) -> None:
        """Send logging message to the client.

        Args:
            type: Type of logging message. Can be 'info', 'debug', 'warning' or 'error'.
            message: Contents of the message.
        """
        self.send(Message.log(type, message))

    def execute(
        self, jsfunction: JSFunction, args: list[Any], store: str | None = None
    ) -> None:
        """Execute a JS function."""
        # Define function if not defined yet
        if jsfunction.id not in self._functions:
            self.send(Message.function(jsfunction.id, jsfunction.args, jsfunction.body))
            self._functions.add(jsfunction.id)
        # Execute function with given arguments
        self.send(Message.execute(jsfunction.id, args, store))

    async def flush(self) -> None:
        """Send all queued messages."""
        # Host files
        for url, path in self._queue_files:
            self._server.add_file(url, path)
        self._queue_files = []

        # Set upload callbacks
        for url, callback in self._queue_upload_callbacks:
            self._server.add_upload_callback(url, callback)
        self._queue_upload_callbacks = []

        # Send all messages
        for data in self._queue_messages:
            await self._client.send(data)
        self._queue_messages = []

    def host(self, path: Path) -> str:
        """Expose file via web server.

        Returns:
            URL at which the resource can be accessed.
        """
        url = f"/tmp/{random_id()}"
        self._queue_files.append((url, path))
        return url

    def create_upload_gate(self, handler: Handler[UploadEvent]) -> str:
        """Add callback for file upload.

        Returns:
            URL to which the files must be uploaded.
        """
        url = f"/upload/{random_id()}"

        async def async_callback(event: UploadEvent) -> None:
            self.call_handler(handler, event)
            await self.flush()

        def callback(event: UploadEvent) -> None:
            self.create_task(async_callback(event))

        self._queue_upload_callbacks.append((url, callback))
        return url

    def call_handler(self, handler: Handler[T], event: T) -> None:
        """Call event handler in the context of the session."""
        num_params = len(inspect.signature(handler).parameters)

        if num_params != 0 and num_params != 1:
            raise RuntimeError("Handler must haves 0 or 1 parameters")

        # Call handler with session context
        token = Session._current.set(self)
        try:
            result = handler(*[event][:num_params])  # type: ignore[call-arg]
        finally:
            Session._current.reset(token)

        # If handler is async, create task
        if inspect.isawaitable(result):
            self.create_task(result)

    def create_task(self, task: Awaitable[None]) -> None:
        """Create task in the context of the session."""

        async def wrapper(session: Session, task: Awaitable[None]) -> None:
            token = Session._current.set(session)
            await task
            await session.flush()
            Session._current.reset(token)

        asyncio.create_task(wrapper(self, task))

    def __enter__(self) -> None:
        self._token = Session._current.set(self)

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: object | None,
    ) -> None:
        Session._current.reset(self._token)

    def set_theme(self, theme: Literal["light", "dark"]) -> None:
        self.send(Message("theme", theme=theme))

    def set_title(self, title: str) -> None:
        """Set document title."""
        self.send(Message("title", title=title))


# Attributes


class Attr(property):
    """The `Attr` class represents an attribute of an element."""

    def __init__(self, name: str) -> None:
        super().__init__(self._get, self._set)
        self._name = name
        self._private = "_" + name

    def _get(self, elem: Elem):
        return getattr(elem, self._private)

    def _set(self, elem: Elem, value: Any):
        setattr(elem, self._private, value)
        elem._update_attrs({self._name: value})

    @property
    def name(self) -> str:
        return self._name


# Mounting events


class MountEvent:
    """Event that fires when an element is mounted."""


class UnmountEvent:
    """Event that fires when an element is unmounted."""


# Elements


class Elem:
    """Base element class. All elements and components derive from this class."""

    def __init__(
        self,
        tag: str,
        *children: Elem | str | list[Elem | str],
        **attrs: Any,
    ) -> None:
        self._tag = tag
        self._children: list[Elem | str] = []
        for child in children:
            if isinstance(child, list):
                self._children.extend(child)
            elif isinstance(child, Elem) or isinstance(child, str):
                self._children.append(child)
            else:
                raise TypeError(f"Invalid child type: {type(child)}")
        self._style: dict[str, str | None] = {}
        self._attrs = attrs
        self._classes: set[str] = set()

        self._id = random_id()
        self._parent: Elem | None = None

        self._onmount_handlers: list[Handler[MountEvent]] = []
        self._onunmount_handlers: list[Handler[UnmountEvent]] = []

        # Set parent of children
        for child in self._children:
            if isinstance(child, Elem):
                child._parent = self

    @property
    def id(self) -> str:
        """Element id."""
        return self._id

    @property
    def tag(self) -> str:
        """Element tag."""
        return self._tag

    @property
    def children(self) -> list[Elem | str]:
        """Element children."""
        return self._children

    @property
    def parent(self) -> Elem | None:
        """Element parent."""
        return self._parent

    def style(self, style: dict[str, str | None]) -> Self:
        """Update style."""
        self._style.update(style)
        self._update_attrs({"style": style})
        return self

    def attrs(self) -> dict[str, Any]:
        """Get attributes."""
        attrs: dict[str, Any] = {
            "tag": self.tag,
            "id": self.id,
            "parent": self.parent.id if self.parent is not None else "body",
            **self._attrs,
        }

        # Style
        if self._style:
            attrs["style"] = self._style

        # Class
        if self._classes:
            attrs["class"] = " ".join(self._classes)

        # Attributes
        for name in dir(type(self)):
            field = getattr(type(self), name)
            if isinstance(field, Attr):
                value = getattr(self, name)
                if value is None:
                    continue
                if callable(value):
                    attrs[field.name] = True
                else:
                    attrs[field.name] = value

        return attrs

    def set_attr(self, name: str, value: str | int = "") -> Self:
        """Set attribute."""
        self._attrs[name] = value
        self._update_attrs({name: value})
        return self

    def remove_attr(self, name: str) -> Self:
        """Remove attribute."""
        if name in self._attrs:
            del self._attrs[name]
            self._update_attrs({name: None})
        return self

    def is_mounted(self) -> bool:
        """Check if element is mounted."""
        return Session.require().get_elem(self.id) is self

    def onmount(self, handler: Handler[MountEvent]) -> Self:
        """Add event handler for mount event."""
        self._onmount_handlers.append(handler)
        return self

    def onunmount(self, handler: Handler[UnmountEvent]) -> Self:
        """Add event handler for unmount event."""
        self._onunmount_handlers.append(handler)
        return self

    def mount(self) -> None:
        """Mount element."""
        session = Session.require()

        # If already mounted, raise exception
        if self.is_mounted():
            raise Exception(f"Element {self.id} already mounted")

        # Send create message
        session.send(Message(event="create", **self.attrs()))

        # Mount children
        for child in self.children:
            if isinstance(child, Elem):
                child.mount()
            else:
                session.send(
                    Message(event="create", parent=self.id, text=child),
                )

        # Mark as mounted
        session._mounted_elems[self.id] = self

        # Call mount event handlers
        for handler in self._onmount_handlers:
            session.call_handler(handler, MountEvent())

    def unmount(self) -> None:
        """Unmount element."""
        session = Session.require()

        # If not yet mounted, raise exception
        if not self.is_mounted():
            raise Exception(f"Element {self.id} was not mounted")

        # Unmount children
        for child in self.children:
            if isinstance(child, Elem):
                child.unmount()

        # Unmark as mounted
        session._mounted_elems.pop(self.id)

        # Send remove message
        session.send(Message.remove(self.id))

        # Call unmount hook
        for handler in self._onunmount_handlers:
            session.call_handler(handler, UnmountEvent())

    def _update_attrs(self, attrs: dict[str, Any]) -> None:
        if (session := Session.current()) is not None and self.is_mounted():
            session.send(Message.update(self.id, **attrs))

    def clear(self) -> None:
        """Unmount all children."""
        if self.is_mounted():
            for child in self.children:
                if isinstance(child, Elem):
                    child.unmount()
            if (session := Session.current()) is not None:
                session.send(Message.clear(self.id))
        self._children = []

    def append(self, *children: Children) -> Self:
        """Append to the children of this element."""
        for child in children:
            if isinstance(child, list):
                self.append(*child)
            elif isinstance(child, Elem) or isinstance(child, str):
                self._append_elem(child)
            else:
                raise TypeError(f"Object of type {type(child)} cannot be appended")
        return self

    def _append_elem(self, elem: Elem | str) -> None:
        """Append element or string to the children of this element."""
        if isinstance(elem, Elem):
            # Set parent and children variables
            if elem._parent is not None:
                elem._parent._children.remove(elem)
            elem._parent = self
            self._children.append(elem)

            # Set update
            if (session := Session.current()) is not None and self.is_mounted():
                # If elem is not mounted yet, mount it
                if not elem.is_mounted():
                    elem.mount()
                else:
                    # Otherwise, send update message with new `parent` value
                    session.send(Message.update(elem.id, parent=self.id))

        if isinstance(elem, str):
            self._children.append(elem)
            # Append text
            if (session := Session.current()) is not None and self.is_mounted():
                session.send(Message("create", parent=self.id, text=elem))

    def insert(self, position: int, elem: Elem) -> Self:
        """Insert element to the children of this element at given position."""
        # Set parent and children variables
        if elem._parent is not None:
            elem._parent._children.remove(elem)
        elem._parent = self
        self._children.insert(position, elem)

        # Set update
        if (session := Session.current()) is not None and self.is_mounted():
            # If elem is not mounted yet, mount it
            if not elem.is_mounted():
                elem.mount()

            # Send position
            session.send(Message.update(elem.id, parent=self.id, position=position))
        return self

    def contains(self, elem: Elem) -> bool:
        """Check if element is contained by this element."""
        return elem._parent is self or (
            elem._parent is not None and self.contains(elem._parent)
        )

    @property
    def text(self) -> str:
        """Element text contents."""
        return "".join(
            child if isinstance(child, str) else child.text for child in self._children
        )

    @text.setter
    def text(self, value: str) -> None:
        self._children = [value]
        self._update_attrs({"text": value})

    def set_text(self, text: str) -> Self:
        self._children = [text]
        self._update_attrs({"text": text})
        return self

    def __repr__(self) -> str:
        s = ""
        s += f"<{self.tag}>\n"
        for child in self._children:
            if isinstance(child, str):
                s += f"  {child}\n"
            else:
                s += "\n".join([f"  {line}" for line in repr(child).split("\n")])
                s += "\n"
        s += f"</{self.tag}>"
        return s

    def add_class(self, name: str) -> Self:
        """Add class."""
        self._classes.update(name.split(" "))
        self._update_attrs({"class": " ".join(self._classes)})
        return self

    def remove_class(self, name: str) -> Self:
        """Remove class."""
        for name in name.split(" "):
            if name in self._classes:
                self._classes.remove(name)
        self._update_attrs({"class": " ".join(self._classes)})
        return self


# Types

Children: TypeAlias = Elem | str | list[Elem | str]
