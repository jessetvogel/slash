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


# Events


class ClickEvent:
    def __init__(self, target: Elem) -> None:
        self._target = target

    @property
    def target(self) -> Elem:
        return self._target


ClickEventHandler = Callable[[ClickEvent], None]


class SupportsOnClick:
    def __init__(self, onclick: ClickEventHandler | None = None) -> None:
        self._onclick = onclick

    def click(self, event: ClickEvent) -> None:
        """Trigger click event."""
        if self._onclick:
            self._onclick(event)

    def onclick(self, handler: ClickEventHandler | None) -> None:
        self._onclick = handler

    def attrs(self) -> dict[str, Any]:
        return {"onclick": True} if self._onclick else {}


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
    def __init__(self, oninput: InputEventHandler | None = None) -> None:
        self._oninput = oninput

    def input(self, event: InputEvent) -> None:
        """Trigger input event."""
        if self._oninput:
            self._oninput(event)

    def oninput(self, handler: InputEventHandler | None) -> None:
        self._oninput = handler

    def attrs(self) -> dict[str, Any]:
        return {"oninput": True} if self._oninput else {}


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
    def __init__(self, onchange: ChangeEventHandler | None = None) -> None:
        self._onchange = onchange

    def change(self, event: ChangeEvent) -> None:
        """Trigger change event."""
        if self._onchange:
            self._onchange(event)

    def onchange(self, handler: ChangeEventHandler | None) -> None:
        self._onchange = handler

    def attrs(self) -> dict[str, Any]:
        return {"onchange": True} if self._onchange else {}


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
        self.update_attrs({"style": style})

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

    def build(self) -> None:
        # Check for context
        if self.id in self.client._elems:
            raise Exception("element already build")

        # Construct message
        attrs: dict[str, Any] = {}
        for base in type(self).mro():
            if hasattr(base, "attrs") and callable(base.attrs):
                attrs |= base.attrs(self)
        self.client.send(Message(event="create", **attrs))

        # Build children
        for child in self.children:
            if isinstance(child, Elem):
                child.build()
            else:
                self.client.send(
                    Message(event="create", tag="text", parent=self.id, text=child)
                )

        # Mark as added
        self.client._elems.add(self.id)

        # Call mount
        self.mount()

    def update_attrs(self, attrs: dict[str, Any]) -> None:
        self.client.send(Message.update(self.id, **attrs))

    def mount(self) -> None:
        pass

    def unmount(self) -> None:
        pass

    def remove(self) -> None:
        self.unmount()
        self.client.send(Message.remove(self.id))

    def clear(self) -> None:
        self.client.send(Message.clear(self.id))

    def append(self, elem: Elem) -> None:
        if elem.parent:
            # TODO: remove element from its old parent, without unmounting it!
            return

        elem._parent = self

        if self._context is not None:
            elem.set_context(self._context)
            elem.build()

    @property
    def text(self) -> str:
        return "".join(
            child if isinstance(child, str) else child.text for child in self._children
        )

    @text.setter
    def text(self, value: str) -> None:
        self._children = [value]
        self.update_attrs({"text": value})

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


class Div(Elem, SupportsOnClick):
    def __init__(
        self,
        children: Children = None,
        *,
        style: dict[str, str] | None = None,
        onclick: ClickEventHandler | None = None,
    ) -> None:
        super().__init__("div", children=children, style=style)
        SupportsOnClick.__init__(self, onclick)


class P(Elem, SupportsOnClick):
    def __init__(
        self,
        children: Children = None,
        *,
        style: dict[str, str] | None = None,
        onclick: ClickEventHandler | None = None,
    ) -> None:
        super().__init__("p", children=children, style=style)
        SupportsOnClick.__init__(self, onclick)


class Span(Elem, SupportsOnClick):
    def __init__(
        self,
        children: Children = None,
        *,
        style: dict[str, str] | None = None,
        onclick: ClickEventHandler | None = None,
    ) -> None:
        super().__init__("span", children=children, style=style)
        SupportsOnClick.__init__(self, onclick)


class H1(Elem, SupportsOnClick):
    def __init__(
        self,
        children: Children = None,
        *,
        style: dict[str, str] | None = None,
        onclick: ClickEventHandler | None = None,
    ) -> None:
        super().__init__("h1", children=children, style=style)
        SupportsOnClick.__init__(self, onclick)


class H2(Elem, SupportsOnClick):
    def __init__(
        self,
        children: Children = None,
        *,
        style: dict[str, str] | None = None,
        onclick: ClickEventHandler | None = None,
    ) -> None:
        super().__init__("h2", children=children, style=style)
        SupportsOnClick.__init__(self, onclick)


class H3(Elem, SupportsOnClick):
    def __init__(
        self,
        children: Children = None,
        *,
        style: dict[str, str] | None = None,
        onclick: ClickEventHandler | None = None,
    ) -> None:
        super().__init__("h3", children=children, style=style)
        SupportsOnClick.__init__(self, onclick)


class H4(Elem, SupportsOnClick):
    def __init__(
        self,
        children: Children = None,
        *,
        style: dict[str, str] | None = None,
        onclick: ClickEventHandler | None = None,
    ) -> None:
        super().__init__("h4", children=children, style=style)
        SupportsOnClick.__init__(self, onclick)


class H5(Elem, SupportsOnClick):
    def __init__(
        self,
        children: Children = None,
        *,
        style: dict[str, str] | None = None,
        onclick: ClickEventHandler | None = None,
    ) -> None:
        super().__init__("h5", children=children, style=style)
        SupportsOnClick.__init__(self, onclick)


class H6(Elem, SupportsOnClick):
    def __init__(
        self,
        children: Children = None,
        *,
        style: dict[str, str] | None = None,
        onclick: ClickEventHandler | None = None,
    ) -> None:
        super().__init__("h6", children=children, style=style)
        SupportsOnClick.__init__(self, onclick)


class A(Elem, SupportsOnClick):
    def __init__(
        self,
        children: Children = None,
        *,
        href: str = "#",
        style: dict[str, str] | None = None,
        onclick: ClickEventHandler | None = None,
    ) -> None:
        super().__init__("a", children=children, style=style)
        SupportsOnClick.__init__(self, onclick)
        self._href = href

    @property
    def href(self) -> str:
        return self._href

    @href.setter
    def href(self, value: str) -> None:
        self._href = value
        self.update_attrs({"href": self.href})

    def attrs(self) -> dict[str, Any]:
        return {"href": self.href}


class Button(Elem, SupportsOnClick):
    def __init__(
        self,
        children: Children = None,
        *,
        style: dict[str, str] | None = None,
        onclick: ClickEventHandler | None = None,
    ) -> None:
        super().__init__("button", children=children, style=style)
        SupportsOnClick.__init__(self, onclick)


class Input(Elem, SupportsOnClick, SupportsOnInput, SupportsOnChange):
    def __init__(
        self,
        type: str = "text",
        *,
        style: dict[str, str] | None = None,
        placeholder: str = "",
        onclick: ClickEventHandler | None = None,
        oninput: InputEventHandler | None = None,
        onchange: ChangeEventHandler | None = None,
    ) -> None:
        super().__init__("input", style=style)
        SupportsOnClick.__init__(self, onclick)
        SupportsOnInput.__init__(self, oninput)
        SupportsOnChange.__init__(self, onchange)
        self._type = type
        self._placeholder = placeholder

    @property
    def type(self) -> str:
        return self._type

    @property
    def placeholder(self) -> str:
        return self._placeholder

    def attrs(self) -> dict[str, Any]:
        return {"type": self.type, "placeholder": self.placeholder}


class Textarea(Elem, SupportsOnClick, SupportsOnInput, SupportsOnChange):
    def __init__(
        self,
        text: str = "",
        *,
        style: dict[str, str] | None = None,
        placeholder: str = "",
        onclick: ClickEventHandler | None = None,
        oninput: InputEventHandler | None = None,
        onchange: ChangeEventHandler | None = None,
    ) -> None:
        super().__init__("textarea", [text], style=style)
        SupportsOnClick.__init__(self, onclick)
        SupportsOnInput.__init__(self, oninput)
        SupportsOnChange.__init__(self, onchange)
        self._placeholder = placeholder

    @property
    def placeholder(self) -> str:
        return self._placeholder

    def attrs(self) -> dict[str, Any]:
        return {"placeholder": self.placeholder}
