from slash.core import ChangeEvent, Elem, SupportsOnChange
from slash import html


class Tabs(Elem, SupportsOnChange):
    def __init__(self, labels: list[str], *, value: str | None = None) -> None:
        super().__init__(
            "div",
            [
                html.Div(label).onclick(lambda event: self._onclick_tab(event.target))
                for label in labels
            ],
            **{"class": "slash-tabs"},  # type: ignore[arg-type]
        )
        SupportsOnChange.__init__(self)
        self._labels = labels
        self._value: str = value or labels[0]

        for child in self.children:
            if isinstance(child, Elem) and child.text == value:
                child.add_class("selected")

    def _onclick_tab(self, tab: Elem) -> None:
        self.value = tab.text

    @property
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, value_: str) -> None:
        if hasattr(self, "_value") and value_ == self._value:
            return
        self._value = value_
        for child in self.children:
            if isinstance(child, Elem):
                if child.text == self.value:
                    child.add_class("selected")
                else:
                    child.remove_class("selected")
        self.change(ChangeEvent(self, self.value))
