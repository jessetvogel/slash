from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Self

from slash.basic.svg import SVG, SVGElem
from slash.core import Elem


class Pie(SVG):
    def __init__(self, *, width: int = 384, height: int = 256) -> None:
        super().__init__()

        self._width = width
        self._height = height

        self.style({"display": "block"})
        self.set_attr("width", width)
        self.set_attr("height", height)

        self.title = None
        self.legend = True
        self.radius = 96.0
        self.gap = 0.0

    @property
    def title(self) -> str | None:
        return self._title

    @title.setter
    def title(self, title: str | None) -> None:
        self._title = title

    def set_title(self, title: str | None) -> Self:
        self.title = title
        return self

    @property
    def legend(self) -> bool:
        return self._legend

    @legend.setter
    def legend(self, legend: bool) -> None:
        self._legend = legend

    def set_legend(self, legend: bool) -> Self:
        self.legend = legend
        return self

    @property
    def gap(self) -> float:
        return self._gap

    @gap.setter
    def gap(self, gap: float) -> None:
        self._gap = max(gap, 0.0)

    def set_gap(self, gap: float) -> Self:
        self.gap = gap
        return self

    @property
    def radius(self) -> float:
        return self._radius

    @radius.setter
    def radius(self, radius: float) -> None:
        self._radius = max(radius, 0.0)

    def set_radius(self, radius: float) -> Self:
        self.radius = radius
        return self

    def render(self, labels: Sequence[str], values: Sequence[float]) -> Self:
        self.clear()

        total = sum(values)

        u, v = self._width / 2, self._height / 2
        r, g = self.radius, self.gap

        self.append(style := Elem("style"))

        if self.title is not None:
            self.append(
                SVGElem(
                    "text",
                    self.title,
                    **{
                        "x": self._width / 2,
                        "y": 24,
                        "text-anchor": "middle",
                        "dominant-baseline": "auto",
                        "font-size": "18px",
                    },
                )
            )

        theta = -math.pi / 2.0
        for label, value in zip(labels, values):
            percent = value / total * 100.0
            d_theta = value / total * 2.0 * math.pi

            color = self._next_color()

            self.append(
                path := SVGElem(
                    "path",
                    d=(
                        f"M {u + g * math.cos(theta)} {v + g * math.sin(theta)} "  # noqa: E501
                        f"L {u + r * math.cos(theta)} {v + r * math.sin(theta)} "  # noqa: E501
                        f"A {r} {r} 0 0 1 {u + r * math.cos(theta + d_theta)} {v + r * math.sin(theta + d_theta)} "  # noqa: E501
                        f"L {u + g * math.cos(theta + d_theta)} {v + g * math.sin(theta + d_theta)} "  # noqa: E501
                        f"A {g} {g} 0 0 0 {u + g * math.cos(theta)} {v + g * math.sin(theta)} "  # noqa: E501
                        "Z"
                    ),
                    fill=color,
                    stroke="none",
                )
            )

            style.append(
                f"#{path.id}:hover {{ opacity: 0.8; }}"
                f"#{path.id} {{ transition: opacity 0.2s; }}"
            )

            text_anchor = "start" if math.cos(theta + d_theta / 2.0) < 0.0 else "end"

            self.append(
                SVGElem(
                    "text",
                    label,
                    x=8 if text_anchor == "start" else self._width - 8,
                    y=v + (r - 8) * math.sin(theta + d_theta / 2.0) - 4,
                )
                .style({"font-size": "14px"})
                .set_attr("text-anchor", text_anchor)
            )

            self.append(
                SVGElem(
                    "text",
                    f"{percent:.1f}%",
                    x=8 if text_anchor == "start" else self._width - 8,
                    y=v + (r - 8) * math.sin(theta + d_theta / 2.0) + 4,
                )
                .style({"font-size": "14px", "opacity": "0.5"})
                .set_attr("text-anchor", text_anchor)
                .set_attr("dominant-baseline", "hanging")
            )

            self.append(
                SVGElem(
                    "line",
                    x1=u + (r - 8) * math.cos(theta + d_theta / 2.0),
                    y1=v + (r - 8) * math.sin(theta + d_theta / 2.0),
                    x2=8 if text_anchor == "start" else self._width - 8,
                    y2=v + (r - 8) * math.sin(theta + d_theta / 2.0),
                    stroke="black",
                ).set_attr("stroke-width", 1)
            )

            theta += d_theta

        return self

    def _update_legend(self) -> None:
        pass

    def _next_color(self) -> str:
        if not hasattr(self, "_color_counter"):
            self._color_counter = 0
        else:
            self._color_counter += 1
        colors = ["var(--blue)", "var(--red)", "var(--yellow)", "var(--green)"]
        return colors[self._color_counter % len(colors)]
