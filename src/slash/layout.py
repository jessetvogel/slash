"""Slash layout components."""

from slash.core import Children, Elem
from slash.events import SupportsOnClick


class Row(Elem, SupportsOnClick):
    """Row element."""

    def __init__(self, *children: Children):
        super().__init__(
            "div",
            *children,
        )
        self.add_class("slash-row")

    @property
    def tag(self) -> str:
        return "div"


class Column(Elem, SupportsOnClick):
    """Column element."""

    def __init__(self, *children: Children):
        super().__init__(
            "div",
            *children,
        )
        self.add_class("slash-column")

    @property
    def tag(self) -> str:
        return "div"


class Panel(Elem):
    """Panel element."""

    def __init__(self, *children: Children):
        super().__init__(
            "div",
            *children,
        )
        self.add_class("slash-panel")
