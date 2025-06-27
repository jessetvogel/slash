from slash.core import Elem, Children


class Row(Elem):
    def __init__(self, children: Children = None):
        super().__init__(
            "div",
            children,
        )
        self.style(
            {
                "display": "flex",
                "flex-direction": "row",
            }
        )

    @property
    def tag(self) -> str:
        return "div"


class Column(Elem):
    def __init__(self, children: Children = None):
        super().__init__(
            "div",
            children,
        )
        self.style(
            {
                "display": "flex",
                "flex-direction": "column",
            }
        )

    @property
    def tag(self) -> str:
        return "div"
