from typing import Self

from slash.core import Elem
from slash.events import ClickEvent, SupportsOnClick


class Checkbox(Elem, SupportsOnClick):
    """Checkbox element.

    Args:
        label: Text label after checkbox.
        checked: Flag indicating if checkbox is checked.
        disabled: Flag indicating if checkbox is disabled.
    """

    def __init__(self, label: str | Elem = "", *, checked: bool = False, disabled: bool = False) -> None:
        super().__init__("label", label)
        self.label = label
        self.checked = checked
        self.disabled = disabled
        self.add_class("slash-checkbox")
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
        if not self.disabled:
            self._checked = not self._checked
            self._update_checked()
