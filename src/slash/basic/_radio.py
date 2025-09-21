from __future__ import annotations

from typing import Self

from slash.core import Elem
from slash.events import ClickEvent, SupportsOnClick


class Radio(Elem, SupportsOnClick):
    """Radio button element.

    Args:
        label: Text label after radio button.
        checked: Flag indicating if radio button is selected.
        disabled: Flag indicating if checkbox is disabled.
    """

    def __init__(self, label: str | Elem = "", *, checked: bool = False, disabled: bool = False) -> None:
        super().__init__("label", label)
        self.label = label
        self.checked = checked
        self.disabled = disabled
        self._connections: list[Radio] = []
        self.add_class("slash-radio")
        self.onclick(self._handle_click)

    @property
    def label(self) -> str | Elem:
        return self._label

    @label.setter
    def label(self, label: str | Elem) -> None:
        self._label = label
        self.clear()
        self.append(label)

    def set_label(self, label: str) -> Self:
        self.label = label
        return self

    @property
    def checked(self) -> bool:
        return self._checked

    @checked.setter
    def checked(self, checked: bool) -> None:
        self._checked = checked
        self._update_checked()

    def set_checked(self, checked: bool) -> Self:
        self.checked = checked
        return self

    @property
    def disabled(self) -> bool:
        return self._disabled

    @disabled.setter
    def disabled(self, disabled: bool) -> None:
        self._disabled = disabled
        self._update_disabled()

    def set_disabled(self, disabled: bool) -> Self:
        self.disabled = disabled
        return self

    def _update_checked(self) -> None:
        (self.add_class if self._checked else self.remove_class)("checked")

    def _update_disabled(self) -> None:
        (self.add_class if self._disabled else self.remove_class)("disabled")

    def _handle_click(self, event: ClickEvent) -> None:
        if not self._checked and not self._disabled:
            self.checked = True
            for connection in self._connections:
                connection.checked = False

    def connect(self, other: Radio) -> Self:
        """Connect to other radio button.

        In a group of connected radio buttons, at most one can be selected at a time.

        Args:
            other: Radio button to connect to.
        """
        if other not in self._connections:
            for connection in self._connections:
                other.connect(connection)
            self._connections.append(other)
            other.connect(self)
        return self
