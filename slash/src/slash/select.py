from slash.core import ChangeEvent, ChangeEventHandler, Elem, SupportsOnChange


class Select(Elem, SupportsOnChange):
    def __init__(
        self, options: list[str], *, onchange: ChangeEventHandler | None = None
    ):
        super().__init__("select", [Elem("option", option) for option in options])
        SupportsOnChange.__init__(self, onchange or (lambda _: None))
        self._value = options[0]

    @property
    def value(self) -> str:
        return self._value

    def change(self, event: ChangeEvent) -> None:
        self._value = event.value
        for child in self.children:
            if isinstance(child, Elem) and child.tag == "option":
                if child.text == self._value:
                    child.set_attr("selected")
                else:
                    child.remove_attr("selected")
        if self.onchange:
            self.onchange(event)
