from __future__ import annotations

from slash.basic._svg import SVG, SVGElem
from slash.core import Elem
from slash.html import Div
from slash.layout import Panel


def test_svg() -> Elem:
    return Div(
        Panel(
            SVG(
                SVGElem(
                    "circle",
                    cx="64",
                    cy="64",
                    r="48",
                    fill="var(--yellow)",
                    stroke="var(--teal)",
                ).set_attr("stroke-width", "4"),
                SVGElem(
                    "circle",
                    cx="0",
                    cy="0",
                    r="64",
                    fill="var(--blue)",
                    stroke="var(--orange)",
                ).set_attr("stroke-width", "4"),
                SVGElem(
                    "circle",
                    cx="128",
                    cy="128",
                    r="64",
                    fill="var(--green)",
                    stroke="var(--aubergine)",
                ).set_attr("stroke-width", "4"),
                SVGElem("text", "SVG TEXT", x=64, y=64)
                .set_attr("text-anchor", "middle")
                .set_attr("dominant-baseline", "middle")
                .set_attr("fill", "var(--pink)"),
                width=128,
                height=128,
            ),
        ),
    )
