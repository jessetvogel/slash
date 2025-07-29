from typing import Any

from slash.core import Children, Elem


class SVGElem(Elem):
    """Analogous to :py:class:`Elem` for SVG elements.

    SVG elements are created with the namespace ``http://www.w3.org/2000/svg``.

    Args:
        tag: HTML tag of the element.
        children: Child or children of element. Either an element, string or
            list of elements and strings.
        attrs: Additional attribute values.
    """

    def __init__(
        self,
        tag: str,
        *children: Children,
        **attrs: Any,
    ):
        super().__init__(tag, *children, **attrs)
        self.set_attr("ns", "http://www.w3.org/2000/svg")


class SVG(SVGElem):
    """HTML ``<svg>`` element."""

    def __init__(self, *children: Children, **attrs: Any):
        super().__init__("svg", *children, **attrs)
        self.set_attr("xmlns", "http://www.w3.org/2000/svg")
