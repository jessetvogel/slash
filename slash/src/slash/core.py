from __future__ import annotations

from abc import abstractmethod
from collections.abc import Callable
import random
import string
from typing import Any

import slash.event
from slash.message import Message


def random_id() -> str:
    characters = string.ascii_letters + string.digits  # A-Z, a-z, 0-9
    return "".join(random.choices(characters, k=8))


class Page:
    def __init__(self, root: Callable[[], Elem]):
        self._root = root()
        self._ids: dict[str, Elem] = {}
        self._message_queue: list[Message] = []

        self.register(self._root)

    def register(self, elem: Elem) -> None:
        """Register element by id."""
        elem.page = self
        self._ids[elem.id] = elem
        for child in elem._children:
            if isinstance(child, Elem):
                self.register(child)

    def find(self, id: str) -> Elem | None:
        """Get element by id."""
        return self._ids.get(id, None)

    def broadcast(self, message: Message) -> None:
        self._message_queue.append(message)

    def poop(self) -> list[Message]:
        queue = self._message_queue
        self._message_queue = []
        return queue

    @property
    def root(self) -> Elem:
        return self._root


# Elements


class Elem:
    def __init__(
        self,
        children: list[Elem | str] | Elem | str | None = None,
        *,
        style: dict[str, str] | None = None,
        onclick: Callable[[MouseEvent], None] | None = None,
        **attrs: Any,
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
        self._onclick = onclick
        self._attrs = attrs

        # Set parent of children
        for child in self._children:
            if isinstance(child, Elem):
                child._parent = self

    @property
    def page(self) -> Page:
        if self._page is None:
            raise Exception("Element has not been registered on page yet")
        return self._page

    @page.setter
    def page(self, page: Page):
        self._page = page
        for child in self._children:
            if isinstance(child, Elem):
                child.page = page

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
        self.page.broadcast(Message.update(self.id, style=style))

    def set_text(self, text: str) -> None:
        self._children = [text]

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

    def click(self, event: MouseEvent) -> None:
        if self._onclick:
            self._onclick(event)

    @abstractmethod
    def create(self) -> list[Message]:
        pass

    def build(self) -> list[Message]:
        messages = self.create()
        for child in self._children:
            if isinstance(child, Elem):
                messages.extend(child.build())
            else:
                messages.append(
                    Message(event="create", tag="text", parent=self.id, text=child)
                )
        return messages


Children = list[Elem | str] | Elem | str | None


class HTML(Elem):
    def __init__(
        self,
        tag: str,
        children: Children = None,
        **attrs: Any,
    ) -> None:
        super().__init__(children, **attrs)
        self._tag = tag

    @property
    def tag(self) -> str:
        return self._tag

    def create(self) -> list[Message]:
        parent = self.parent.id if self.parent is not None else "body"
        return [
            Message.create(
                tag=self.tag,
                id=self.id,
                parent=parent,
                style=self.style,
                onclick=True,
                **self._attrs,
            )
        ]

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


class Div(HTML):
    def __init__(self, children: Children = None, **attrs) -> None:
        super().__init__("div", children=children, **attrs)


class Span(HTML):
    def __init__(self, children: Children = None, **attrs) -> None:
        super().__init__("span", children=children, **attrs)


# Events


class MouseEvent:
    def __init__(self, target: Elem):
        self._target = target

    @property
    def target(self) -> Elem:
        return self._target
