from __future__ import annotations


class Elem:
    def __init__(
        self,
        tag: str,
        *,
        children: list[Elem | str] | Elem | str | None = None,
        style: dict[str, str] | None = None,
    ) -> None:
        self.tag = tag
        self.children = children or []
        if not isinstance(self.children, list):
            self.children = [self.children]

        self.style = style or {}

    def __repr__(self) -> str:
        return self._repr()

    def _repr(self, indent: int = 0) -> str:
        ind = " " * indent
        s = ""
        s += f"{ind}<{self.tag}>\n"
        for child in self.children:
            if isinstance(child, str):
                s += f"{ind}  {child}\n"
            else:
                s += f"{child._repr(indent + 2)}\n"
        s += f"{ind}</{self.tag}>"
        return s


Children = list[Elem | str] | Elem | str | None


class Div(Elem):
    def __init__(self, children: Children = None, **args) -> None:
        super().__init__("div", children=children, **args)


class Span(Elem):
    def __init__(self, children: Children = None, **args) -> None:
        super().__init__("span", children=children, **args)
