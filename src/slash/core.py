"""This module contains the Slash core classes."""

from __future__ import annotations

import asyncio
import inspect
from collections.abc import Awaitable, Callable, Mapping, Sequence
from contextvars import ContextVar
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any, Literal, Self, TypeAlias, TypeVar
from urllib.parse import parse_qsl, urlparse

from slash._logging import LOGGER
from slash._message import Message
from slash._server import Client, Server, UploadEvent
from slash._utils import random_id
from slash.js import JSFunction

# Types

T = TypeVar("T")

Handler: TypeAlias = Callable[[T], Awaitable[Any] | Any] | Callable[[], Awaitable[Any] | Any]

# Session


class Session:
    """The `Session` class is used to communicate with the currently-connected user."""

    _current: ContextVar[Session] = ContextVar("session")

    def __init__(self, server: Server, client: Client) -> None:
        """Initialize session instance.

        Args:
            server: Server instance.
            client: Client instance.
        """
        self._server = server
        self._client = client

        self._queue_messages: list[str] = []
        self._queue_files: list[tuple[str, Path]] = []
        self._queue_upload_callbacks: list[tuple[str, Callable[[UploadEvent], None]]] = []

        self._mounted_elems: dict[str, Elem] = {}  # elements that client already has
        self._functions: set[str] = set()  # functions that client already has
        self._root: Elem | None = None

        self._location = Location("")
        self._history = History()

    @staticmethod
    def current() -> Session | None:
        """Get the current session.

        Returns:
            Current session instance or `None`."""
        try:
            return Session._current.get()
        except LookupError:
            pass
        return None

    @staticmethod
    def require() -> Session:
        """Get the current session, or raise an error if there is none.

        Returns:
            Current session instance.

        Raises:
            RuntimeError: If there is no current session."""
        try:
            return Session._current.get()
        except LookupError as err:
            raise RuntimeError("Session required, but no session was set") from err

    @property
    def id(self) -> str:
        """Session id."""
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
                self.send(Message(event="cookie", name="SLASH_SESSION", value=id, days=1))
            self._id = id
        return self._id

    @property
    def location(self) -> Location:
        """Session location instance."""
        return self._location

    @property
    def history(self) -> History:
        """Session history instance."""
        return self._history

    def set_root(self, root: Elem) -> None:
        """Set root element.

        Args:
            root: Element to set as root element.
        """
        if self._root is not None:
            self._root.unmount()
        self._root = root
        root.mount()

    def get_elem(self, id: str) -> Elem | None:
        """Get element by id.

        Args:
            id: Element id.

        Returns:
            Element with given id or `None` if no such element exists.
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
        self,
        type: Literal["info", "debug", "warning", "error"],
        message: str,
        *,
        format: Literal["text", "html"] = "text",
    ) -> None:
        """Send logging message to the client.

        Args:
            type: Type of logging message. Either 'info', 'debug', 'warning' or 'error'.
            message: Contents of the message.
            format: Either 'text' or 'html'.
        """
        self.send(Message.log(type, message, format))

    def execute(self, jsfunction: JSFunction, args: list[Any], name: str | None = None) -> None:
        """Execute a JavaScript function.

        Args:
            jsfunction: JavaScript function instance to execute.
            args: List of arguments to provide to the function.
            name: If set, the output of the function will be stored on the client under this name.
                The output can later be accessed in JavaScript using ``Slash.value(name)``.
        """
        # Define function if not defined yet
        if jsfunction.id not in self._functions:
            self.send(Message.function(jsfunction.id, jsfunction.params, jsfunction.body))
            self._functions.add(jsfunction.id)
        # Execute function with given arguments
        self.send(Message.execute(jsfunction.id, args, name))

    async def flush(self) -> None:
        """Send all queued messages to the client."""
        # Host files
        for url, path in self._queue_files:
            self._server.share_file(url, path)
        self._queue_files = []

        # Set upload callbacks
        for url, callback in self._queue_upload_callbacks:
            self._server.accept_file(url, callback)
        self._queue_upload_callbacks = []

        # Send all messages (including flush event)
        self.send(Message("flush"))
        for data in self._queue_messages:
            await self._client.send(data)

        self._queue_messages = []

    def share_file(self, path: Path) -> str:
        """Create a download endpoint for a local file.

        The file at the given `path` will be served to anyone who accesses the returned URL.

        Args:
            path: Path to the local file to be made accessable.

        Returns:
            URL from which the file can be accessed.
        """
        url = f"/tmp/{random_id()}"
        self._queue_files.append((url, path))
        return url

    def accept_file(self, handler: Handler[UploadEvent]) -> str:
        """Create an endpoint for file uploading.

        Args:
            handler: Handler to be called when files are upload.

        Returns:
            URL to which files can be uploaded.
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
        """Call event handler in the context of the session.

        Args:
            handler: Event handler to execute.
            event: Event to be passed to handler.
        """
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
        """Create task in the context of the session.

        Args:
            task: Awaitable function to run.
        """

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
        """Set theme.

        Args:
            theme: Either 'light' or 'dark'.
        """
        self.send(Message("theme", theme=theme))

    def set_title(self, title: str) -> None:
        """Set document title.

        Args:
            title: Document title.
        """
        self.send(Message("title", title=title))

    def add_stylesheet(self, path: Path) -> None:
        """Add stylesheet.

        Args:
            path: Path to stylesheet.
        """
        url = f"/style/{random_id()}.css"
        self._server.share_file(url, path)
        self.send(
            Message.create(tag="link", id=random_id(), parent="head", rel="stylesheet", type="text/css", href=url)
        )

    def add_script(self, path: Path) -> None:
        """Add script.

        Args:
            path: Path to script.
        """
        url = f"/style/{random_id()}.js"
        self._server.share_file(url, path)
        self.send(Message.create(tag="script", id=random_id(), parent="head", type="text/javascript", src=url))

    def set_location(self, url: str) -> None:
        """Navigate to location.

        Args;
            url: URL to navigate to.
        """
        self.send(Message(event="location", url=url))

    def set_data(self, key: str, value: str | None) -> None:
        """Set value in local storage.

        Args:
            key: Data entry key.
            value: Data entry value. If `None`, then the key is removed.
        """
        self._client.localstorage_set(key, value)
        self.send(Message("data", key=key, value=value))

    def get_data(self, key: str) -> str | None:
        """Get value in local storage.

        Args:
            key: Data entry key.

        Returns:
            Data entry value.
        """
        return self._client.localstorage_get(key)


# Attributes


class Attr(property):
    """Property class representing an attribute of an element.

    Args:
        name: Name of the attribute.
    """

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
    """Event that fires when an element is mounted.

    Args:
        target: Element that was mounted.
    """

    def __init__(self, target: Elem) -> None:
        self._target = target

    @property
    def target(self) -> Elem:
        """Element that was mounted."""
        return self._target


class UnmountEvent:
    """Event that fires when an element is unmounted.

    Args:
        target: Element that was unmounted.
    """

    def __init__(self, target: Elem) -> None:
        self._target = target

    @property
    def target(self) -> Elem:
        """Element that was unmounted."""
        return self._target


# Elements


class Elem:
    """Base class for all Slash elements.

    Args:
        tag: HTML tag of the element.
        children: Child or children of element. Either an element, string or
            list of elements and strings.
        attrs: Additional attribute values.
    """

    def __init__(
        self,
        tag: str,
        *children: Elem | str | Sequence[Elem | str],
        **attrs: str | int,
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
        return self._id

    @property
    def tag(self) -> str:
        return self._tag

    @property
    def children(self) -> list[Elem | str]:
        return list(self._children)

    @property
    def parent(self) -> Elem | None:
        """Parent of element, or ``None`` if the element is the root element."""
        return self._parent

    def style(self, style: Mapping[str, str | None]) -> Self:
        """Update CSS style of element.

        Args:
            style: Mapping with CSS attributes as keys. If a value is a string,
                the CSS attribute is set to that value. If a value is `None`, the
                CSS attribute is reset.
        """
        self._style.update(style)
        self._update_attrs({"style": dict(style)})
        return self

    def attrs(self) -> dict[str, Any]:
        """Get element attributes.

        Returns:
            Dictionary containing the element attributes.
        """
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
        """Set attribute of element.

        Args:
            name: Attribute name.
            value: Attribute value.
        """
        self._attrs[name] = value
        self._update_attrs({name: value})
        return self

    def remove_attr(self, name: str) -> Self:
        """Remove attribute from element.

        Args:
            name: Attribute name.
        """
        if name in self._attrs:
            del self._attrs[name]
            self._update_attrs({name: None})
        return self

    def is_mounted(self) -> bool:
        """Check if element is mounted.

        Returns:
            Boolean indicating if element is mounted.
        """
        return Session.require().get_elem(self.id) is self

    def onmount(self, handler: Handler[MountEvent]) -> Self:
        """Add event handler for mount event.

        Args:
            handler: Handler to be called when element is mounted.
        """
        self._onmount_handlers.append(handler)
        return self

    def onunmount(self, handler: Handler[UnmountEvent]) -> Self:
        """Add event handler for unmount event.

        Args:
            handler: Handler to be called when element is unmounted.
        """
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
            session.call_handler(handler, MountEvent(self))

    def unmount(self, *, reset_parent: bool = True) -> None:
        """Unmount element.

        Args:
            reset_parent: Flag indicating whether parent should be reset.
        """
        session = Session.require()

        # If not yet mounted, raise exception
        if not self.is_mounted():
            raise Exception(f"Element {self.id} was not mounted")

        # Unmount children
        for child in self.children:
            if isinstance(child, Elem):
                child.unmount(reset_parent=False)

        # Reset parent
        if reset_parent:
            self._parent = None

        # Unmark as mounted
        session._mounted_elems.pop(self.id)

        # Send remove message
        session.send(Message.remove(self.id))

        # Call unmount hook
        for handler in self._onunmount_handlers:
            session.call_handler(handler, UnmountEvent(self))

    def _update_attrs(self, attrs: dict[str, Any]) -> None:
        """Send message to client to update attribute values."""
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
        else:
            for child in self.children:
                if isinstance(child, Elem):
                    child._parent = None
        self._children = []

    def append(self, *children: Children) -> Self:
        """Append to the children of this element.

        Args:
            children: Child or children to append. Either an element, string or list of elements and strings.
        """
        for child in children:
            if isinstance(child, list):
                self.append(*child)
            elif isinstance(child, Elem) or isinstance(child, str):
                self._append_or_insert_elem(child)
            else:
                raise TypeError(f"Object of type {type(child)} cannot be appended")
        return self

    def insert(self, position: int, *children: Children) -> Self:
        """Insert into the children of this element at given position.

        Args:
            position: Index before which to insert children.
            children: Child or children to append. Either an element, string or list of elements and strings.
        """
        offset = 0
        for child in children:
            if isinstance(child, list):
                self.insert(position + offset, *child)
                offset += len(child)
            elif isinstance(child, Elem) or isinstance(child, str):
                self._append_or_insert_elem(child, position=position + offset)
                offset += 1
            else:
                raise TypeError(f"Object of type {type(child)} cannot be inserted")
        return self

    def _append_or_insert_elem(self, elem: Elem | str, *, position: int | None = None) -> None:
        """Append or insert element or string to the children of this element."""
        if isinstance(elem, Elem):
            # Set parent and children variables
            if elem._parent is not None:
                elem._parent._children.remove(elem)
            elem._parent = self
            self._children.insert(position if position is not None else len(self._children), elem)

            if (session := Session.current()) is not None and self.is_mounted():
                # If elem is not mounted yet, mount it
                if not elem.is_mounted():
                    elem.mount()
                # Otherwise, set new `parent` value (case `position` is none)
                elif position is None:
                    session.send(Message.update(elem.id, parent=self.id))
                # If `position` is not none, send parent and position
                if position is not None:
                    session.send(Message.update(elem.id, parent=self.id, position=position))

        if isinstance(elem, str):
            # Append or insert text
            self._children.insert(position if position is not None else len(self._children), elem)
            if (session := Session.current()) is not None and self.is_mounted():
                if position is not None:
                    session.send(Message("create", parent=self.id, text=elem))
                else:
                    session.send(Message("create", parent=self.id, text=elem, position=position))

    def contains(self, elem: Elem) -> bool:
        """Check if another element is contained by this element.

        Args:
            elem: The other element.

        Returns:
            Boolean indicating if this element contains the other element.
        """
        return elem._parent is self or (elem._parent is not None and self.contains(elem._parent))

    @property
    def text(self) -> str:
        """Element text contents."""
        return "".join(child if isinstance(child, str) else child.text for child in self._children)

    @text.setter
    def text(self, text: str) -> None:
        self.clear()
        self.append(text)

    def set_text(self, text: str) -> Self:
        """Set the text content of the element."""
        self.text = text
        return self

    def __repr__(self) -> str:
        """HTML representation of element."""
        parts = []
        parts.append(f"<{self.tag}>")
        for child in self._children:
            if isinstance(child, str):
                parts.append(child)
            else:
                parts.append(repr(child))
        parts.append(f"</{self.tag}>")
        return "".join(parts)

    def add_class(self, name: str) -> Self:
        """Add one or more classes to element.

        Args:
            name: Name of class to add. Multiple names may be provided separated by spaces.
        """
        self._classes.update(name.split(" "))
        self._update_attrs({"class": " ".join(self._classes)})
        return self

    def remove_class(self, name: str) -> Self:
        """Remove one or more classes from element.

        Args:
            name: Name of class to add. Multiple names may be provided separated by spaces.
        """
        for name in name.split(" "):
            if name in self._classes:
                self._classes.remove(name)
        self._update_attrs({"class": " ".join(self._classes)})
        return self


# Types

Children: TypeAlias = Elem | str | Sequence[Elem | str]


# History


@dataclass
class PopStateEvent:
    state: Any


class History:
    """Class representing the JavaScript ``window.history`` object."""

    def __init__(self) -> None:
        self._onpopstate_handlers: list[Handler[PopStateEvent]] = []

    def go(self, delta: int) -> None:
        """Call the JavaScript ``window.history.go`` method."""
        Session.require().send(Message(event="history", go=delta))

    def forward(self) -> None:
        """Call the JavaScript ``window.history.forward`` method."""
        self.go(1)

    def back(self) -> None:
        """Call the JavaScript ``window.history.back`` method."""
        self.go(-1)

    def push(self, state: Any, url: str | None = None) -> None:
        """Call the JavaScript ``window.history.pushState`` method.

        Args:
            state: State to set. Must be JSON serializable.
            url: URL to set.
        """
        Session.require().send(Message(event="history", push=state, url=url))

    def replace(self, state: Any, url: str | None = None) -> None:
        """Call the JavaScript ``window.history.replaceState`` method.

        Args:
            state: State to set. Must be JSON serializable.
            url: URL to set.
        """
        Session.require().send(Message(event="history", replace=state, url=url))

    def onpopstate(self, handler: Handler[PopStateEvent]) -> None:
        """Add event handler for `popstate` event.

        Args:
            handler: Handler to call on `popstate` event.
        """
        self._onpopstate_handlers.append(handler)

    def popstate(self, event: PopStateEvent) -> None:
        """Trigger `popstate` event.

        Args:
            event: Popstate event to be passed to handlers.
        """
        session = Session.require()
        for handler in self._onpopstate_handlers:
            session.call_handler(handler, event)


# Location


class Location:
    """Class containing detailed information on client location."""

    def __init__(self, url: str) -> None:
        """Initialize location from URL.

        Args:
            url: URL of location.
        """
        result = urlparse(url, allow_fragments=True)

        self._url = url
        self._scheme = result.scheme
        self._host = result.netloc
        self._path = result.path
        self._query = dict(parse_qsl(result.query))
        self._fragment = result.fragment

        if ":" in self._host:
            hostname, port = self._host.split(":")
            self._hostname = hostname
            self._port = int(port)
        else:
            self._hostname = self._host
            self._port = 80

    @property
    def url(self) -> str:
        """URL of location."""
        return self._url

    @property
    def scheme(self) -> str:
        """Scheme of location, such as ``http`` or ``https``."""
        return self._scheme

    @property
    def host(self) -> str:
        """Host of location, such as ``127.0.0.1:8080``."""
        return self._host

    @property
    def hostname(self) -> str:
        """Hostname of location, such as ``127.0.0.1``."""
        return self._hostname

    @property
    def port(self) -> int:
        """Port of location, such as ``8080``."""
        return self._port

    @property
    def path(self) -> str:
        """Path of location, such as ``/path``."""
        return self._path

    @property
    def query(self) -> Mapping[str, str]:
        """Query of location as key value mapping."""
        return MappingProxyType(self._query)

    @property
    def fragment(self) -> str:
        """Fragment of location, that is the part after the ``#`` character."""
        return self._fragment
