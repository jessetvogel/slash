from __future__ import annotations

from collections.abc import Callable
from typing import Any

from slash.client import Client
from slash.message import Message
from slash.utils import random_id


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

    @property
    def name(self) -> str:
        return self._name


# Events


class ClickEvent:
    def __init__(self, target: Elem) -> None:
        self._target = target

    @property
    def target(self) -> Elem:
        return self._target


ClickEventHandler = Callable[[ClickEvent], None]


class SupportsOnClick:
    onclick = Attr("onclick")

    def __init__(self, onclick: ClickEventHandler | None = None) -> None:
        self.onclick = onclick

    def click(self, event: ClickEvent) -> None:
        """Trigger click event."""
        if self.onclick:
            self.onclick(event)


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


InputEventHandler = Callable[[InputEvent], None]


class SupportsOnInput:
    oninput = Attr("oninput")

    def __init__(self, oninput: InputEventHandler | None = None) -> None:
        self.oninput = oninput

    def input(self, event: InputEvent) -> None:
        """Trigger input event."""
        if self.oninput:
            self.oninput(event)


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


ChangeEventHandler = Callable[[ChangeEvent], None]


class SupportsOnChange:
    onchange = Attr("onchange")

    def __init__(self, onchange: ChangeEventHandler | None = None) -> None:
        self.onchange = onchange

    def change(self, event: ChangeEvent) -> None:
        """Trigger change event."""
        if self.onchange:
            self.onchange(event)


# Elements


class Elem:
    def __init__(
        self,
        tag: str,
        children: list[Elem | str] | Elem | str | None = None,
        *,
        style: dict[str, str] | None = None,
        **attrs: Any,
    ) -> None:
        self._tag = tag
        if children is None:
            children = []
        if not isinstance(children, list):
            children = [children]
        self._children = children
        self._style = style or {}
        self._attrs = attrs

        self._id = random_id()
        self._context: Context | None = None
        self._parent: Elem | None = None

        # Set parent of children
        for child in self._children:
            if isinstance(child, Elem):
                child._parent = self

    @property
    def tag(self) -> str:
        return self._tag

    @property
    def children(self) -> list[Elem | str]:
        return self._children

    @property
    def style(self) -> dict[str, str]:
        return self._style

    @style.setter
    def style(self, style: dict[str, str]) -> None:
        self._style.update(style)
        self._update_attrs({"style": style})

    @property
    def id(self) -> str:
        return self._id

    @property
    def parent(self) -> Elem | None:
        return self._parent

    def attrs(self) -> dict[str, Any]:
        attrs: dict[str, Any] = {
            "tag": self.tag,
            "id": self.id,
            "parent": self.parent.id if self.parent is not None else "body",
            **self._attrs,
        }

        if self.style:
            attrs["style"] = self.style

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

    @property
    def client(self) -> Client:
        if self._context is None:
            raise Exception("element has no context")
        if self._context.client is None:
            raise Exception("no current client")
        return self._context.client

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

        # Call mount hook
        self.onmount()

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
        self.onunmount()

    def onmount(self) -> None:
        pass

    def onunmount(self) -> None:
        pass

    def _update_attrs(self, attrs: dict[str, Any]) -> None:
        if self._context:
            self.client.send(Message.update(self.id, **attrs))

    def clear(self) -> None:
        self.client.send(Message.clear(self.id))

    def append(self, elem: Elem) -> None:
        if self._context is None:
            raise Exception("element has no context")
        elem.set_context(self._context)

        # If elem is not mounted yet, set its parent and mount it
        if not elem.is_mounted():
            elem._parent = self
            elem.mount()
            return

        # Otherwise, set its parent and send update message
        elem._parent = self
        self.client.send(Message.update(elem.id, parent=self.id))

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


Children = list[Elem | str] | Elem | str | None
