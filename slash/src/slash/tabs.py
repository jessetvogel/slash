from slash.core import Elem
from slash import html


class Tabs(Elem):
    def __init__(self, labels: list[str], *, selected: int = 0) -> None:
        super().__init__(
            "div",
            [html.Div(label) for label in labels],
            style={"display": "flex", "flex-direction": "row", "gap": "16px"},
        )
        self._labels = labels
