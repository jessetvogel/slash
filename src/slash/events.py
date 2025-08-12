"""This module contains the Slash event classes."""

from __future__ import annotations

import sys
from typing import Self

from slash._server import UploadedFile, UploadEvent
from slash.core import Elem, Handler, MountEvent, Session, UnmountEvent


class ClickEvent:
    """Event that fires when an element is clicked.

    Args:
        target: Element that was clicked.
    """

    def __init__(self, target: Elem) -> None:
        self._target = target

    @property
    def target(self) -> Elem:
        """Element that was clicked."""
        return self._target


class SupportsOnClick:
    """Mix-in class for `onclick` support."""

    @property
    def onclick_handlers(self) -> list[Handler[ClickEvent]]:
        if not hasattr(self, "_onclick_handlers"):
            self._onclick_handlers: list[Handler[ClickEvent]] = []
        return self._onclick_handlers

    def onclick(self, handler: Handler[ClickEvent]) -> Self:
        """Add event handler for click event.

        Args:
            handler: Function to be called when a click event is fired.
        """
        assert isinstance(self, Elem)
        self.onclick_handlers.append(handler)
        self.set_attr("onclick", True)
        return self

    def click(self, event: ClickEvent) -> None:
        """Trigger click event.

        Args:
            event: Click event instance to be passed to handlers.
        """
        assert isinstance(self, Elem)
        session = Session.require()
        for handler in self.onclick_handlers:
            session.call_handler(handler, event)


class InputEvent:
    """Event that fires when the editable content of an element is updated.

    Args:
        target: Element whose content was updated.
        value: Value of the updated content.
    """

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
    """Mix-in class for `oninput` support."""

    @property
    def oninput_handlers(self) -> list[Handler[InputEvent]]:
        if not hasattr(self, "_oninput_handlers"):
            self._oninput_handlers: list[Handler[InputEvent]] = []
        return self._oninput_handlers

    def oninput(self, handler: Handler[InputEvent]) -> Self:
        """Add event handler for input event.

        Args:
            handler: Function to be called when an input event is fired.
        """
        assert isinstance(self, Elem)
        self.oninput_handlers.append(handler)
        self.set_attr("oninput", True)
        return self

    def input(self, event: InputEvent) -> None:
        """Trigger input event.

        Args:
            event: Input event instance to be passed to handlers.
        """
        assert isinstance(self, Elem)
        session = Session.require()
        for handler in self.oninput_handlers:
            session.call_handler(handler, event)


class ChangeEvent:
    """Event that fires when the editable content of an element is changed.

    Args:
        target: Element whose content was changed.
        value: Value of the changed content.
    """

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
    """Mix-in class for `onchange` support."""

    @property
    def onchange_handlers(self) -> list[Handler[ChangeEvent]]:
        if not hasattr(self, "_onchange_handlers"):
            self._onchange_handlers: list[Handler[ChangeEvent]] = []
        return self._onchange_handlers

    def onchange(self, handler: Handler[ChangeEvent]) -> Self:
        """Add event handler for change event.

        Args:
            handler: Function to be called when a change event is fired.
        """
        assert isinstance(self, Elem)
        self.onchange_handlers.append(handler)
        self.set_attr("onchange", True)
        return self

    def change(self, event: ChangeEvent) -> None:
        """Trigger change event.

        Args:
            event: Change event instance to be passed to handlers.
        """
        assert isinstance(self, Elem)
        session = Session.require()
        for handler in self.onchange_handlers:
            session.call_handler(handler, event)


# So that these events can be imported from `slash.events`
__all__ = [
    name for name, obj in vars(sys.modules[__name__]).items() if isinstance(obj, type) and obj.__module__ == __name__
]
__all__ += ["UploadEvent", "UploadedFile", "MountEvent", "UnmountEvent"]
