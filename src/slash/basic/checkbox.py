from typing import Self

from slash.core import Elem
from slash.events import ClickEvent, SupportsOnClick


class Checkbox(Elem, SupportsOnClick):
    def __init__(self, label: str = "", *, checked: bool = False) -> None:
        super().__init__("label", label)
        self._label = label
        self._checked = checked
        self.add_class("slash-checkbox")
        self.onclick(self._handle_click)

    @property
    def label(self) -> str:
        return self._label

    @label.setter
    def label(self, label: str) -> None:
        self.set_text(label)

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

    def _update_checked(self) -> None:
        if self._checked:
            self.add_class("checked")
        else:
            self.remove_class("checked")

    def _handle_click(self, event: ClickEvent) -> None:
        self._checked = not self._checked
        self._update_checked()
