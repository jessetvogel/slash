from __future__ import annotations

from abc import abstractmethod
from collections.abc import Callable
import random
import string
from typing import Any

from slash.client import Client
from slash.message import Message


def random_id() -> str:
    characters = string.ascii_letters + string.digits  # A-Z, a-z, 0-9
    return "_" + "".join(random.choices(characters, k=8))


class Page:
    def __init__(self, root: Callable[[], Elem]) -> None:
        self._root = root()
        self._ids: dict[str, Elem] = {}
        self._client: Client | None = None

        self.register(self._root)

    def register(self, elem: Elem) -> None:
        """Register element by id."""
        elem.set_page(self)
        self._ids[elem.id] = elem
        for child in elem._children:
            if isinstance(child, Elem):
                self.register(child)

    def find(self, id: str) -> Elem | None:
        """Get element by id."""
        return self._ids.get(id, None)

    @property
    def root(self) -> Elem:
        return self._root

    @property
    def client(self) -> Client:
        if self._client is None:
            raise Exception("Currently no client")
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
        children: list[Elem | str] | Elem | str | None = None,
        *,
        style: dict[str, str] | None = None,
    ) -> None:
        self._page: Page | None = None
        self._parent: Elem | None = None
        self._id = random_id()
        if children is None:
            children = []
        if not isinstance(children, list):
            children = [children]
        self._children = children
        self._style = style or {}

        # Set parent of children
        for child in self._children:
            if isinstance(child, Elem):
                child._parent = self

    @property
    def client(self) -> Client:
        if self._page is None:
            raise Exception("Element is not on a page")
        return self._page.client

    def set_page(self, page: Page) -> None:
        self._page = page
        for child in self._children:
            if isinstance(child, Elem):
                child.set_page(page)

    @property
    def children(self) -> list[Elem | str]:
        return self._children

    @property
    def id(self) -> str:
        return self._id

    @property
    def parent(self) -> Elem | None:
        return self._parent

    @property
    def style(self) -> dict[str, str]:
        return self._style

    @style.setter
    def style(self, style: dict[str, str]) -> None:
        self._style.update(style)
        self.update_attrs({"style": style})

    def set_text(self, text: str) -> None:
        self._children = [text]
        self.update_attrs({"text": text})

    def get_text(self) -> str:
        return "".join(
            child if isinstance(child, str) else child.text for child in self._children
        )

    @property
    def text(self) -> str:
        return self.get_text()

    @text.setter
    def text(self, value: str) -> None:
        self.set_text(value)

    @property
    @abstractmethod
    def tag(self) -> str:
        pass

    def attrs(self) -> dict[str, Any]:
        attrs: dict[str, Any] = {
            "tag": self.tag,
            "id": self.id,
            "parent": self.parent.id if self.parent is not None else "body",
        }
        if self.style:
            attrs["style"] = self.style
        return attrs

    def create(self) -> Message:
        attrs: dict[str, Any] = {}
        for base in type(self).mro():
            if hasattr(base, "attrs") and callable(base.attrs):
                attrs |= base.attrs(self)
        return Message(event="create", **attrs)

    def update_attrs(self, attrs: dict[str, Any]) -> None:
        self.client.reply(Message.update(self.id, **attrs))

    def mount(self) -> None:
        pass

    def unmount(self) -> None:
        pass

    def remove(self) -> None:
        self.unmount()
        self.client.reply(Message.remove(self.id))


Children = list[Elem | str] | Elem | str | None


class HTML(Elem):
    def __init__(
        self,
        tag: str,
        children: Children = None,
        *,
        style: dict[str, Any] | None = None,
        **attrs: Any,
    ) -> None:
        super().__init__(children, style=style)
        self._tag = tag
        self._attrs = attrs

    @property
    def tag(self) -> str:
        return self._tag

    def attrs(self) -> dict[str, Any]:
        return self._attrs

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


class Div(HTML, SupportsOnClick):
    def __init__(
        self,
        children: Children = None,
        *,
        style: dict[str, str] | None = None,
        onclick: ClickEventHandler | None = None,
    ) -> None:
        super().__init__("div", children=children, style=style)
        SupportsOnClick.__init__(self, onclick)


class P(HTML, SupportsOnClick):
    def __init__(
        self,
        children: Children = None,
        *,
        style: dict[str, str] | None = None,
        onclick: ClickEventHandler | None = None,
    ) -> None:
        super().__init__("p", children=children, style=style)
        SupportsOnClick.__init__(self, onclick)


class Span(HTML, SupportsOnClick):
    def __init__(
        self,
        children: Children = None,
        *,
        style: dict[str, str] | None = None,
        onclick: ClickEventHandler | None = None,
    ) -> None:
        super().__init__("span", children=children, style=style)
        SupportsOnClick.__init__(self, onclick)


class H1(HTML, SupportsOnClick):
    def __init__(
        self,
        children: Children = None,
        *,
        style: dict[str, str] | None = None,
        onclick: ClickEventHandler | None = None,
    ) -> None:
        super().__init__("h1", children=children, style=style)
        SupportsOnClick.__init__(self, onclick)


class H2(HTML, SupportsOnClick):
    def __init__(
        self,
        children: Children = None,
        *,
        style: dict[str, str] | None = None,
        onclick: ClickEventHandler | None = None,
    ) -> None:
        super().__init__("h2", children=children, style=style)
        SupportsOnClick.__init__(self, onclick)


class H3(HTML, SupportsOnClick):
    def __init__(
        self,
        children: Children = None,
        *,
        style: dict[str, str] | None = None,
        onclick: ClickEventHandler | None = None,
    ) -> None:
        super().__init__("h3", children=children, style=style)
        SupportsOnClick.__init__(self, onclick)


class H4(HTML, SupportsOnClick):
    def __init__(
        self,
        children: Children = None,
        *,
        style: dict[str, str] | None = None,
        onclick: ClickEventHandler | None = None,
    ) -> None:
        super().__init__("h4", children=children, style=style)
        SupportsOnClick.__init__(self, onclick)


class H5(HTML, SupportsOnClick):
    def __init__(
        self,
        children: Children = None,
        *,
        style: dict[str, str] | None = None,
        onclick: ClickEventHandler | None = None,
    ) -> None:
        super().__init__("h5", children=children, style=style)
        SupportsOnClick.__init__(self, onclick)


class H6(HTML, SupportsOnClick):
    def __init__(
        self,
        children: Children = None,
        *,
        style: dict[str, str] | None = None,
        onclick: ClickEventHandler | None = None,
    ) -> None:
        super().__init__("h6", children=children, style=style)
        SupportsOnClick.__init__(self, onclick)


class A(HTML, SupportsOnClick):
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


class Button(HTML, SupportsOnClick):
    def __init__(
        self,
        children: Children = None,
        *,
        style: dict[str, str] | None = None,
        onclick: ClickEventHandler | None = None,
    ) -> None:
        super().__init__("button", children=children, style=style)
        SupportsOnClick.__init__(self, onclick)


class Input(HTML, SupportsOnClick, SupportsOnInput, SupportsOnChange):
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


class Textarea(HTML, SupportsOnClick, SupportsOnInput, SupportsOnChange):
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
