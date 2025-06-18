from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
import inspect
from typing import Any, Self, TypeVar

from slash.client import Client
from slash.logging import get_logger
from slash.message import Message
from slash.utils import random_id

LOGGER = get_logger()


class Context:
    def __init__(self) -> None:
        self._client: Client | None = None
        self._elems: dict[str, Elem] = {}

    def add_elem(self, elem: Elem) -> None:
        """Register element by id."""
        self._elems[elem.id] = elem

    def get_elem(self, id: str) -> Elem | None:
        """Get element by id."""
        return self._elems.get(id, None)

    @property
    def client(self) -> Client | None:
        """The current active client."""
        return self._client

    @client.setter
    def client(self, value: Client | None) -> None:
        self._client = value

    def call_handler(self, handler: Handler[T], event: T) -> None:
        result = handler(event)
        if inspect.isawaitable(result):
            self.create_task(result)

    def create_task(self, task: Awaitable[None]) -> None:
        async def wrapper(client: Client, task: Awaitable[None]) -> None:
            self.client = client
            await task
            self.client = None
            await client.flush()

        assert self.client is not None
        asyncio.create_task(wrapper(self.client, task))


# Attributes


class Attr(property):
    def __init__(self, name: str) -> None:
        super().__init__(self._get, self._set)
        self._name = name
        self._private = "_" + name

    def _get(self, elem: Elem):
        return getattr(elem, self._private)

    def _set(self, elem: Elem, value: Any):
        setattr(elem, self._private, value)
        elem._update_attrs({self._name: value})

    def set_silently(self, elem: Elem, value: Any):
        setattr(elem, self._private, value)

    @property
    def name(self) -> str:
        return self._name


# Elements


class MountEvent:
    pass


class UnmountEvent:
    pass


class Elem:
    def __init__(
        self,
        tag: str,
        children: list[Elem | str] | Elem | str | None = None,
        **attrs: Any,
    ) -> None:
        self._tag = tag
        if children is None:
            children = []
        if not isinstance(children, list):
            children = [children]
        self._children = children
        self._style: dict[str, str] = {}
        self._attrs = attrs
        self._classes: set[str] = set()

        self._id = random_id()
        self._context: Context | None = None
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
        return self._children

    @property
    def parent(self) -> Elem | None:
        return self._parent

    @property
    def client(self) -> Client:
        if self._context is None:
            raise Exception("element has no context")
        if self._context.client is None:
            raise Exception("no current client")
        return self._context.client

    def style(self, style: dict[str, str]) -> Self:
        self._style.update(style)
        self._update_attrs({"style": style})
        return self

    def attrs(self) -> dict[str, Any]:
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

        # Indicate whether to set event handlers
        if isinstance(self, SupportsOnClick) and self.has_onclick_handlers():
            attrs["onclick"] = True
        if isinstance(self, SupportsOnChange) and self.has_onchange_handlers():
            attrs["onchange"] = True
        if isinstance(self, SupportsOnInput) and self.has_oninput_handlers():
            attrs["oninput"] = True

        return attrs

    def set_attr(self, name: str, value: str = "") -> None:
        self._attrs[name] = value
        self._update_attrs({name: value})

    def remove_attr(self, name: str) -> None:
        if name in self._attrs:
            del self._attrs[name]
            self._update_attrs({name: None})

    def set_context(self, context: Context) -> None:
        """Set context, and of children."""
        if self._context is not context:
            self._context = context
            self._context.add_elem(self)
            for child in self._children:
                if isinstance(child, Elem):
                    child.set_context(context)

    def is_mounted(self) -> bool:
        return self.id in self.client._mounted_elems

    def onmount(self, handler: Handler[MountEvent]) -> Self:
        self._onmount_handlers.append(handler)
        return self

    def onunmount(self, handler: Handler[UnmountEvent]) -> Self:
        self._onunmount_handlers.append(handler)
        return self

    def mount(self) -> None:
        # If already mounted, raise exception
        if self.is_mounted():
            raise Exception(f"Element {self.id} already mounted")

        # Send create message
        self.client.send(Message(event="create", **self.attrs()))

        # Mount children
        for child in self.children:
            if isinstance(child, Elem):
                child.mount()
            else:
                self.client.send(
                    Message(event="create", tag="text", parent=self.id, text=child),
                )

        # Mark as mounted
        self.client._mounted_elems.add(self.id)

        # Call mount event handlers
        for handler in self._onmount_handlers:
            handler(MountEvent())

    def unmount(self) -> None:
        # If not yet mounted, raise exception
        if not self.is_mounted():
            raise Exception(f"Element {self.id} was not mounted")

        # Unmount children
        for child in self.children:
            if isinstance(child, Elem):
                child.unmount()

        # Unmark as mounted
        self.client._mounted_elems.remove(self.id)

        # Send remove message
        self.client.send(Message.remove(self.id))

        # Call unmount hook
        for handler in self._onunmount_handlers:
            handler(UnmountEvent())

    def _update_attrs(self, attrs: dict[str, Any]) -> None:
        if self._context:
            self.client.send(Message.update(self.id, **attrs))

    def clear(self) -> None:
        for child in self.children:
            if isinstance(child, Elem):
                child.unmount()
        self._children = []

    def append(self, elem: Elem) -> Self:
        # Set parent and children variables
        if elem._parent is not None:
            elem._parent._children.remove(elem)
        elem._parent = self
        self._children.append(elem)

        # Set context
        if self._context is not None:
            elem.set_context(self._context)

            # If elem is not mounted yet, set its parent and mount it
            if not elem.is_mounted():
                elem._parent = self
                elem.mount()
            else:
                # Otherwise, set its parent and send update message
                self.client.send(Message.update(elem.id, parent=self.id))

        return self

    def contains(self, elem: Elem) -> bool:
        return elem._parent is self or (
            elem._parent is not None and self.contains(elem._parent)
        )

    @property
    def text(self) -> str:
        return "".join(
            child if isinstance(child, str) else child.text for child in self._children
        )

    @text.setter
    def text(self, value: str) -> None:
        self._children = [value]
        self._update_attrs({"text": value})

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
        self._classes.update(name.split(" "))
        self._update_attrs({"class": " ".join(self._classes)})
        return self

    def remove_class(self, name: str) -> Self:
        for name in name.split(" "):
            if name in self._classes:
                self._classes.remove(name)
        self._update_attrs({"class": " ".join(self._classes)})
        return self


Children = list[Elem | str] | Elem | str | None

# Events

T = TypeVar("T")
Handler = Callable[[T], Awaitable[None] | None]


class ClickEvent:
    def __init__(self, target: Elem) -> None:
        self._target = target

    @property
    def target(self) -> Elem:
        return self._target


class SupportsOnClick:
    @property
    def onclick_handlers(self) -> list[Handler[ClickEvent]]:
        if not hasattr(self, "_onclick_handlers"):
            self._onclick_handlers: list[Handler[ClickEvent]] = []
        return self._onclick_handlers

    def onclick(self, handler: Handler[ClickEvent]) -> Self:
        """Add click event handler."""
        self.onclick_handlers.append(handler)
        return self

    def click(self, event: ClickEvent) -> None:
        """Trigger click event."""
        assert isinstance(self, Elem) and self._context is not None
        for handler in self.onclick_handlers:
            self._context.call_handler(handler, event)

    def has_onclick_handlers(self) -> bool:
        return bool(self.onclick_handlers)


class InputEvent:
    def __init__(self, target: Elem, value: str) -> None:
        self._target = target
        self._value = value

    @property
    def target(self) -> Elem:
        return self._target

    @property
    def value(self) -> str:
        return self._value


class SupportsOnInput:
    @property
    def oninput_handlers(self) -> list[Handler[InputEvent]]:
        if not hasattr(self, "_oninput_handlers"):
            self._oninput_handlers: list[Handler[InputEvent]] = []
        return self._oninput_handlers

    def oninput(self, handler: Handler[InputEvent]) -> Self:
        """Add input event handler."""
        self.oninput_handlers.append(handler)
        return self

    def input(self, event: InputEvent) -> None:
        """Trigger input event."""
        for handler in self.oninput_handlers:
            handler(event)

    def has_oninput_handlers(self) -> bool:
        return bool(self.oninput_handlers)


class ChangeEvent:
    def __init__(self, target: Elem, value: str) -> None:
        self._target = target
        self._value = value

    @property
    def target(self) -> Elem:
        return self._target

    @property
    def value(self) -> str:
        return self._value


class SupportsOnChange:
    @property
    def onchange_handlers(self) -> list[Handler[ChangeEvent]]:
        if not hasattr(self, "_onchange_handlers"):
            self._onchange_handlers: list[Handler[ChangeEvent]] = []
        return self._onchange_handlers

    def onchange(self, handler: Handler[ChangeEvent]) -> Self:
        """Add change event handler."""
        self.onchange_handlers.append(handler)
        return self

    def change(self, event: ChangeEvent) -> None:
        """Trigger change event."""
        for handler in self.onchange_handlers:
            handler(event)

    def has_onchange_handlers(self) -> bool:
        return bool(self.onchange_handlers)
