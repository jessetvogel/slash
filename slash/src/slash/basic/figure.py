from __future__ import annotations

import math
from abc import abstractmethod
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Self

from slash.basic.svg import SVG, SVGElem


@dataclass
class View:
    x_min: float = 0.0
    x_max: float = 1.0
    y_min: float = 0.0
    y_max: float = 1.0
    u_min: float = 0.0
    u_max: float = 1.0
    v_min: float = 0.0
    v_max: float = 1.0


class Figure(SVG):
    def __init__(self, *, width: int = 384, height: int = 256) -> None:
        super().__init__()

        self._width = width
        self._height = height

        self.style({"display": "block"})
        self.set_attr("width", width)
        self.set_attr("height", height)

        self.title = None
        self.xlabel = None
        self.ylabel = None
        self.legend = False
        self.grid = False
        self.xlim = None, None
        self.ylim = None, None

        self._view = View()
        self._plots: list[Plot] = []

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
    def xlabel(self) -> str | None:
        return self._xlabel

    @xlabel.setter
    def xlabel(self, xlabel: str | None) -> None:
        self._xlabel = xlabel

    def set_xlabel(self, xlabel: str | None) -> Self:
        self.xlabel = xlabel
        return self

    @property
    def ylabel(self) -> str | None:
        return self._ylabel

    @ylabel.setter
    def ylabel(self, ylabel: str | None) -> None:
        self._ylabel = ylabel

    def set_ylabel(self, ylabel: str | None) -> Self:
        self.ylabel = ylabel
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
    def grid(self) -> bool:
        return self._grid

    @grid.setter
    def grid(self, grid: bool) -> None:
        self._grid = grid

    def set_grid(self, grid: bool) -> Self:
        self.grid = grid
        return self

    @property
    def xlim(self) -> tuple[float | None, float | None]:
        return self._xmin, self._xmax

    @xlim.setter
    def xlim(self, xlim: tuple[float | None, float | None]) -> None:
        self._xmin, self._xmax = xlim

    def set_xlim(self, xmin: float | None = None, xmax: float | None = None) -> Self:
        self.xlim = xmin, xmax
        return self

    @property
    def ylim(self) -> tuple[float | None, float | None]:
        return self._ymin, self._ymax

    @ylim.setter
    def ylim(self, ylim: tuple[float | None, float | None]) -> None:
        self._ymin, self._ymax = ylim

    def set_ylim(self, ymin: float | None = None, ymax: float | None = None) -> Self:
        self.ylim = ymin, ymax
        return self

    def add_plot(self, plot: Plot) -> Self:
        if plot.color is None:
            plot.color = self._next_color()

        self._plots.append(plot)
        return self

    def remove_plot(self, plot: Plot) -> Self:
        self._plots.remove(plot)
        return self

    def clear_plots(self) -> Self:
        self._plots.clear()
        return self

    def render(self) -> Self:
        self._update_view()
        self._update_defs()
        self._update_grid()
        self._update_plots()
        self._update_axes()
        self._update_ticks()
        self._update_labels()
        self._update_legend()
        return self

    def _update_plots(self) -> None:
        if not hasattr(self, "_svg_plots"):
            self._svg_plots = SVGElem("g")
            self.append(self._svg_plots)

        self._svg_plots.set_attr("clip-path", f"url(#{self._clip_plots_id})")

        self._svg_plots.clear()
        for plot in self._plots:
            plot.plot(self._svg_plots, self._xy_to_uv)

    def _update_view(self) -> None:
        self._view.v_max = 40 if self.title is not None else 16
        self._view.v_min = (
            self._height - 48 if self.xlabel is not None else self._height - 16
        )
        self._view.u_min = 48 if self.ylabel is not None else 16
        self._view.u_max = self._width - 16

        self._view.x_min = self.xlim[0] or min(x for p in self._plots for x in p.xs)
        self._view.x_max = self.xlim[1] or max(x for p in self._plots for x in p.xs)
        self._view.y_min = self.ylim[0] or min(y for p in self._plots for y in p.ys)
        self._view.y_max = self.ylim[1] or max(y for p in self._plots for y in p.ys)

    def _update_defs(self) -> None:
        if not hasattr(self, "_svg_defs"):
            self._svg_defs = SVGElem("defs")
            self.append(self._svg_defs)

        self._svg_defs.clear()
        self._svg_defs.append(
            clip := SVGElem(
                "clipPath",
                SVGElem(
                    "rect",
                    x=self._view.u_min,
                    y=self._view.v_max,
                    width=self._view.u_max - self._view.u_min,
                    height=self._view.v_min - self._view.v_max,
                ),
            )
        )
        self._clip_plots_id: str = clip.id

    def _update_axes(self) -> None:
        if not hasattr(self, "_svg_axes"):
            self._svg_axes = SVGElem(
                "polyline",
                fill="none",
                **{"stroke": "black", "stroke-width": "1"},
            )
            self.append(self._svg_axes)

        self._svg_axes.set_attr(
            "points",
            " ".join(
                [
                    f"{self._view.u_min},{self._view.v_max}",
                    f"{self._view.u_min},{self._view.v_min}",
                    f"{self._view.u_max},{self._view.v_min}",
                ]
            ),
        )

    def _update_legend(self) -> None:
        if not hasattr(self, "_svg_legend"):
            self._svg_legend = SVGElem("g", **{"font-size": "14px"})
            self.append(self._svg_legend)

        self._svg_legend.clear()

        if not self.legend:
            return

        y_top = self._view.v_max + 8
        x_left = self._view.u_max - 8 - 128
        x_right = self._view.u_max - 8

        self._svg_legend.append(
            bg := SVGElem(
                "rect",
                x=x_left,
                y=y_top,
                rx=4,
                ry=4,
                width=x_right - x_left,
                height=0,
                fill="rgba(255, 255, 255, 0.67)",
                stroke="#ccc",
            )
        )

        y_current = y_top + 12

        for plot in self._plots:
            if plot.label is not None:
                self._svg_legend.append(
                    SVGElem(
                        "circle", cx=x_left + 12, cy=y_current, r=4, fill=plot.color
                    )
                )
                self._svg_legend.append(
                    SVGElem(
                        "text",
                        plot.label,
                        x=x_left + 12 + 12,
                        y=y_current,
                        **{"text-anchor": "start", "dominant-baseline": "middle"},
                    )
                )
                y_current += 16

        y_bottom = y_current - 16 + 12

        bg.set_attr("height", int(y_bottom - y_top))

    def _xy_to_uv(self, x: float, y: float) -> tuple[float, float]:
        """Convert abstract xy-coordinates to SVG uv-coordinates."""
        u = self._view.u_min + (self._view.u_max - self._view.u_min) * (
            x - self._view.x_min
        ) / (self._view.x_max - self._view.x_min)
        v = self._view.v_min + (self._view.v_max - self._view.v_min) * (
            y - self._view.y_min
        ) / (self._view.y_max - self._view.y_min)
        return u, v

    def _update_ticks(self) -> None:
        if not hasattr(self, "_svg_ticks"):
            self._svg_ticks = SVGElem("g", **{"stroke": "black", "stroke-width": "1"})
            self.append(self._svg_ticks)

        self._svg_ticks.clear()

        labels = SVGElem("g").style(
            {
                "font-size": "10px",
                "stroke-width": "0",
            }
        )

        for x in self.xticks():
            u, v = self._xy_to_uv(x, self._view.y_min)
            self._svg_ticks.append(SVGElem("line", x1=u, y1=v - 2, x2=u, y2=v + 2))
            labels.append(
                SVGElem(
                    "text",
                    f"{x:.1f}",
                    x=u,
                    y=v + 4,
                    **{"text-anchor": "middle", "dominant-baseline": "hanging"},
                )
            )

        for y in self.yticks():
            u, v = self._xy_to_uv(self._view.x_min, y)
            self._svg_ticks.append(SVGElem("line", x1=u - 2, y1=v, x2=u + 2, y2=v))
            labels.append(
                SVGElem(
                    "text",
                    f"{y:.1f}",
                    x=u - 4,
                    y=v,
                    **{"text-anchor": "end", "dominant-baseline": "middle"},
                )
            )

        self._svg_ticks.append(labels)
        self._svg_ticks.append(labels)

    def _update_grid(self) -> None:
        if not hasattr(self, "_svg_grid"):
            self._svg_grid = SVGElem("g", **{"stroke": "#ccc", "stroke-width": "1"})
            self.append(self._svg_grid)

        self._svg_grid.clear()
        if not self.grid:
            return

        for x in self.xticks():
            u, _ = self._xy_to_uv(x, 0)
            self._svg_grid.append(
                SVGElem("line", x1=u, y1=self._view.v_min, x2=u, y2=self._view.v_max)
            )
        for y in self.yticks():
            _, v = self._xy_to_uv(0, y)
            self._svg_grid.append(
                SVGElem("line", x1=self._view.u_min, y1=v, x2=self._view.u_max, y2=v)
            )

    def _update_labels(self) -> None:
        if not hasattr(self, "_svg_labels"):
            self._svg_labels = SVGElem("g")
            self.append(self._svg_labels)

        self._svg_labels.clear()

        if self.title:
            self._svg_labels.append(
                SVGElem(
                    "text",
                    self.title,
                    **{
                        "x": (self._view.u_min + self._view.u_max) / 2,
                        "y": (self._view.v_max - 16),
                        "text-anchor": "middle",
                        "dominant-baseline": "auto",
                        "font-size": "18px",
                    },
                )
            )

        if self.xlabel:
            self._svg_labels.append(
                SVGElem(
                    "text",
                    self.xlabel,
                    **{
                        "x": (self._view.u_min + self._view.u_max) / 2,
                        "y": (self._view.v_min + 24),
                        "text-anchor": "middle",
                        "dominant-baseline": "hanging",
                        "font-size": "14",
                    },
                )
            )

        if self.ylabel:
            self._svg_labels.append(
                SVGElem(
                    "text",
                    self.ylabel,
                    **{
                        "y": (self._view.u_min - 32),
                        "x": -(self._view.v_min + self._view.v_max) / 2,
                        "text-anchor": "middle",
                        "dominant-baseline": "auto",
                        "font-size": "14",
                        "transform": "rotate(-90)",
                    },
                )
            )

    def xticks(self) -> list[float]:
        interval = round_125((self._view.x_max - self._view.x_min) / 10)
        x = math.ceil(self._view.x_min / interval) * interval
        ticks = [x]
        while x + interval <= self._view.x_max:
            x += interval
            ticks.append(x)
        return ticks

    def yticks(self) -> list[float]:
        interval = round_125((self._view.y_max - self._view.y_min) / 10)
        y = math.ceil(self._view.y_min / interval) * interval
        ticks = [y]
        while y + interval <= self._view.y_max:
            y += interval
            ticks.append(y)
        return ticks

    def _next_color(self) -> str:
        if not hasattr(self, "_color_counter"):
            self._color_counter = 0
        else:
            self._color_counter += 1
        colors = ["var(--blue)", "var(--red)", "var(--yellow)", "var(--green)"]
        return colors[self._color_counter % len(colors)]


def round_125(x: float) -> float:
    if x == 0:
        return 0
    e = math.floor(math.log10(abs(x)))
    b = abs(x) / 10**e
    r = 1 if b < 1.5 else 2 if b < 3.5 else 5 if b < 7.5 else 1
    e += b >= 7.5
    return math.copysign(r * 10**e, x)


@dataclass
class Plot:
    xs: Sequence[float]
    ys: Sequence[float]
    color: str | None = None
    label: str | None = None

    @abstractmethod
    def plot(
        self, frame: SVGElem, xy_to_uv: Callable[[float, float], tuple[float, float]]
    ) -> None:
        pass


@dataclass
class Graph(Plot):
    def plot(
        self, frame: SVGElem, xy_to_uv: Callable[[float, float], tuple[float, float]]
    ):
        points = []
        for x, y in zip(self.xs, self.ys):
            u, v = xy_to_uv(x, y)
            points.append(f"{u},{v}")
        frame.append(
            SVGElem(
                "polyline",
                points=" ".join(points),
                **{"stroke": self.color, "stroke-width": "2", "fill": "none"},
            )
        )


@dataclass
class Scatter(Plot):
    def plot(
        self, frame: SVGElem, xy_to_uv: Callable[[float, float], tuple[float, float]]
    ):
        circles = SVGElem("g", **{"fill": self.color})
        for x, y in zip(self.xs, self.ys):
            u, v = xy_to_uv(x, y)
            circles.append(SVGElem("circle", cx=u, cy=v, r=3))
        frame.append(circles)


@dataclass
class Bar(Plot):
    def plot(
        self, frame: SVGElem, xy_to_uv: Callable[[float, float], tuple[float, float]]
    ):
        bars = SVGElem("g", **{"fill": self.color})

        uvs = [xy_to_uv(x, y) for x, y in zip(self.xs, self.ys)]
        _, z = xy_to_uv(0, 0)

        width = 0.0
        for uv1, uv2 in zip(uvs, uvs[1:]):
            width = max(width, abs(uv2[0] - uv1[0]))

        width *= 0.8

        for x, y in zip(self.xs, self.ys):
            u, v = xy_to_uv(x, y)
            _, z = xy_to_uv(0, 0)
            y, height = min(v, z), abs(z - v)
            bars.append(
                SVGElem("rect", x=u - width / 2, y=y, width=width, height=height)
            )

        frame.append(bars)
