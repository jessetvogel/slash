from __future__ import annotations

from typing import Self

from slash.core import Elem


class Icon(Elem):
    """Icon element.

    Args:
        icon: Icon type, such as :py:const:`info`, :py:const:`warning`, :py:const:`error`,
            :py:const:`debug`, :py:const:`loading`, :py:const:`moon`, :py:const:`sun`.
    """

    def __init__(self, icon: str) -> None:
        super().__init__("span")
        self._icon = icon

        self.add_class(f"slash-icon slash-icon-{icon}")

    @property
    def icon(self) -> str:
        return self._icon

    @icon.setter
    def icon(self, icon: str) -> None:
        self.set_icon(icon)

    def set_icon(self, icon: str) -> Self:
        self.remove_class(f"slash-icon-{self._icon}")
        self.add_class(f"slash-icon-{icon}")
        self._icon = icon
        return self
