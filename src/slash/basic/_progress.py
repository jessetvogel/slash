from slash.core import Elem
from slash.html import Span


class Progress(Elem):
    """Progress bar element.

    Args:
        value: Number between 0 and 1 indicating the progress.
        text: Text in the center of the progress bar. Defaults to the percentage of progress.
    """

    def __init__(self, value: float = 0.0, text: str | None = None):
        super().__init__("div", span := Span())
        self.add_class("slash-progress")
        self._span = span
        self._value = value
        self._text = text
        self.onmount(lambda _: self._update())

    @property
    def value(self) -> float:
        return self._value

    def set_value(self, value: float, text: str | None = None) -> None:
        self._value = max(min(value, 1.0), 0.0)
        self._text = text
        self._update()

    def _update(self) -> None:
        percentage = int(self._value * 100)
        self.style({"--value": f"{percentage}%"})
        self._span.text = self._text if self._text is not None else f"{percentage}%"
        (self.add_class if self._value == 1.0 else self.remove_class)("completed")
