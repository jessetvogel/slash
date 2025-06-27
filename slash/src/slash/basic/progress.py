from slash.core import Elem


class Progress(Elem):
    def __init__(self, text: str | None = None):
        super().__init__("div")
        self.add_class("slash-progress")
        self._value = 0.0
        self._text = text
        self.onmount(lambda _: self._update())

    @property
    def value(self) -> float:
        return self._value

    def set_value(self, value: float, text: str | None = None) -> None:
        self._value = max(min(value, 1.0), 0.0)
        self._text = text
        self._update()

    def _update(self):
        percentage = int(self._value * 100)
        self.style({"--value": f"{percentage}%"})
        self.text = self._text or f"{percentage}%"
        (self.add_class if self._value == 1.0 else self.remove_class)("completed")
