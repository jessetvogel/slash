from __future__ import annotations

from collections.abc import Awaitable
from slash.core import Elem, Session, UnmountEvent, MountEvent

from collections.abc import Callable
from typing import Self, TypeVar

MountEvent
UnmountEvent

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
        assert isinstance(self, Elem)
        self.onclick_handlers.append(handler)
        self.set_attr("onclick", True)
        return self

    def click(self, event: ClickEvent) -> None:
        """Trigger click event."""
        assert isinstance(self, Elem)
        session = Session.require()
        for handler in self.onclick_handlers:
            session.call_handler(handler, event)

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
        assert isinstance(self, Elem)
        self.oninput_handlers.append(handler)
        self.set_attr("oninput", True)
        return self

    def input(self, event: InputEvent) -> None:
        """Trigger input event."""
        assert isinstance(self, Elem)
        session = Session.require()
        for handler in self.oninput_handlers:
            session.call_handler(handler, event)

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
        assert isinstance(self, Elem)
        self.onchange_handlers.append(handler)
        self.set_attr("onchange", True)
        return self

    def change(self, event: ChangeEvent) -> None:
        """Trigger change event."""
        assert isinstance(self, Elem)
        session = Session.require()
        for handler in self.onchange_handlers:
            session.call_handler(handler, event)

    def has_onchange_handlers(self) -> bool:
        return bool(self.onchange_handlers)
