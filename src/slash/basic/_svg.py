from typing import Any

from slash.core import Children, Elem


class SVGElem(Elem):
    def __init__(
        self,
        tag: str,
        *children: Children,
        **attrs: Any,
    ):
        super().__init__(tag, *children, **attrs)
        self.set_attr("ns", "http://www.w3.org/2000/svg")


class SVG(SVGElem):
    def __init__(self, *children: Children, **attrs: Any):
        super().__init__("svg", *children, **attrs)
        self.set_attr("xmlns", "http://www.w3.org/2000/svg")
