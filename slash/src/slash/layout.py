from slash.core import Children, Elem


class Row(Elem):
    def __init__(
        self, children: Children | None = None, *, style: dict[str, str] | None = None
    ):
        super().__init__(
            children,
            style={
                "display": "flex",
                "flex-direction": "row",
            }
            | (style or {}),
        )

    @property
    def tag(self) -> str:
        return "div"


class Column(Elem):
    def __init__(
        self, children: Children | None = None, *, style: dict[str, str] | None = None
    ):
        super().__init__(
            children,
            style={
                "display": "flex",
                "flex-direction": "column",
            }
            | (style or {}),
        )

    @property
    def tag(self) -> str:
        return "div"
