"""Slash events."""

from __future__ import annotations

from typing import Self

from slash._server import UploadEvent
from slash.core import Elem, Handler, MountEvent, Session, UnmountEvent

UploadEvent  # so that `UploadEvent` can be imported from `slash.events`
MountEvent  # so that `MountEvent` can be imported from `slash.events`
UnmountEvent  # so that `UnmountEvent` can be imported from `slash.events`


class ClickEvent:
    """Event that fires when an element is clicked."""

    def __init__(self, target: Elem) -> None:
        self._target = target

    @property
    def target(self) -> Elem:
        """Element that was clicked."""
        return self._target


class SupportsOnClick:
    """Mixin class for onclick support."""

    @property
    def onclick_handlers(self) -> list[Handler[ClickEvent]]:
        if not hasattr(self, "_onclick_handlers"):
            self._onclick_handlers: list[Handler[ClickEvent]] = []
        return self._onclick_handlers

    def onclick(self, handler: Handler[ClickEvent]) -> Self:
        """Add event handler for click event."""
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
    """Event that fires when the editable content of an element is updated."""

    def __init__(self, target: Elem, value: str) -> None:
        self._target = target
        self._value = value

    @property
    def target(self) -> Elem:
        """Element whose content was updated."""
        return self._target

    @property
    def value(self) -> str:
        """Value of the updated content."""
        return self._value


class SupportsOnInput:
    """Mixin class for oninput support."""

    @property
    def oninput_handlers(self) -> list[Handler[InputEvent]]:
        if not hasattr(self, "_oninput_handlers"):
            self._oninput_handlers: list[Handler[InputEvent]] = []
        return self._oninput_handlers

    def oninput(self, handler: Handler[InputEvent]) -> Self:
        """Add event handler for input event."""
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
    """Event that fires when the editable content of an element is changed."""

    def __init__(self, target: Elem, value: str) -> None:
        self._target = target
        self._value = value

    @property
    def target(self) -> Elem:
        """Element whose content was changed."""
        return self._target

    @property
    def value(self) -> str:
        """Value of the changed content."""
        return self._value


class SupportsOnChange:
    """Mixin class for onchange support."""

    @property
    def onchange_handlers(self) -> list[Handler[ChangeEvent]]:
        if not hasattr(self, "_onchange_handlers"):
            self._onchange_handlers: list[Handler[ChangeEvent]] = []
        return self._onchange_handlers

    def onchange(self, handler: Handler[ChangeEvent]) -> Self:
        """Add event handler for change event."""
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
