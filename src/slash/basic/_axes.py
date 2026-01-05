from __future__ import annotations

import math
from abc import ABC, abstractmethod
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from numbers import Real
from typing import Self

from slash._utils import default_color
from slash.basic._svg import SVG, SVGElem
from slash.core import Session
from slash.js import JSFunction


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


_JS_POSITION_LEGEND = JSFunction(
    ["legend_id", "rect_id", "right"],
    """
const l = document.getElementById(legend_id);
const r = document.getElementById(rect_id);
const w = l.getBBox().width;
l.style.transform = `translateX(${right - w}px)`;
r.setAttribute("width", w + 16);
""",
)


class Axes(SVG):
    """Figure with x-axis and y-axis.

    Example:

        >>> from slash.basic import Axes, Graph
        >>>
        >>> axes = Axes()
        >>> axes.add_plot(Graph([0, 1, 2, 3], [42, 37, 96, 51]))
        >>> axes.render()

    Args:
        width: Width of the figure in pixels.
        height: Height of the figure in pixels.
    """

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
        self.set_xticks(None)
        self.set_yticks(None)

        self._view = View()
        self._plots: list[Plot] = []
        self._color_counter = 0

    @property
    def title(self) -> str | None:
        """Title to appear at the top of the figure."""
        return self._title

    @title.setter
    def title(self, title: str | None) -> None:
        self._title = title

    def set_title(self, title: str | None) -> Self:
        self.title = title
        return self

    @property
    def xlabel(self) -> str | None:
        """Description of the x-axis to appear below it."""
        return self._xlabel

    @xlabel.setter
    def xlabel(self, xlabel: str | None) -> None:
        self._xlabel = xlabel

    def set_xlabel(self, xlabel: str | None) -> Self:
        self.xlabel = xlabel
        return self

    @property
    def ylabel(self) -> str | None:
        """Description of the y-axis to appear next to it."""
        return self._ylabel

    @ylabel.setter
    def ylabel(self, ylabel: str | None) -> None:
        self._ylabel = ylabel

    def set_ylabel(self, ylabel: str | None) -> Self:
        self.ylabel = ylabel
        return self

    @property
    def legend(self) -> bool:
        """Flag indicating whether to show legend."""
        return self._legend

    @legend.setter
    def legend(self, legend: bool) -> None:
        self._legend = legend

    def set_legend(self, legend: bool) -> Self:
        self.legend = legend
        return self

    @property
    def grid(self) -> bool:
        """Flag indicating whether to show grid."""
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
        """Add plot to the figure.

        Args:
            plot: Plot instance to add.
        """
        if plot.color is None:
            plot.color = self._next_color()

        self._plots.append(plot)
        return self

    def remove_plot(self, plot: Plot) -> Self:
        self._plots.remove(plot)
        return self

    def clear_plots(self) -> Self:
        """Remove all plots from the figure."""
        self._plots.clear()
        self._color_counter = 0
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
        self._view.v_min = self._height - 48 if self.xlabel is not None else self._height - 24
        self._view.u_min = 48 if self.ylabel is not None else 24
        self._view.u_max = self._width - 16

        def either(a: float | None, b: float) -> float:
            return a if a is not None else b

        if self._plots:
            self._view.x_min = either(self.xlim[0], min(x for p in self._plots for x in p.xs))
            self._view.x_max = either(self.xlim[1], max(x for p in self._plots for x in p.xs))
            self._view.y_min = either(self.ylim[0], min(y for p in self._plots for y in p.ys))
            self._view.y_max = either(self.ylim[1], max(y for p in self._plots for y in p.ys))
        else:
            self._view.x_min = either(self.xlim[0], 0.0)
            self._view.x_max = either(self.xlim[1], self._view.x_min + 1.0)
            self._view.y_min = either(self.ylim[0], 0.0)
            self._view.y_max = either(self.ylim[1], self._view.y_min + 1.0)

        if self._view.x_min == self._view.x_max:
            self._view.x_min -= 0.5
            self._view.x_max += 0.5

        if self._view.y_min == self._view.y_max:
            self._view.y_min -= 0.5
            self._view.y_max += 0.5

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
                **{"stroke": "var(--text)", "stroke-width": "1"},
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
            self._svg_legend = (
                SVGElem("g").set_attr("font-size", "14px").style({"transform": f"translateX({self._width}px)"})
            )
            self.append(self._svg_legend)

        self._svg_legend.clear()

        if not self.legend:
            return

        y_top = self._view.v_max + 8
        x_left = 0

        self._svg_legend.append(
            bg := SVGElem(
                "rect",
                x=x_left,
                y=y_top,
                rx=4,
                ry=4,
                width=0,
                height=0,
                fill="color-mix(in srgb, var(--bg-light) 67%, transparent)",
                stroke="var(--border)",
            )
        )

        y_current = y_top + 12

        for plot in self._plots:
            if plot.label is not None:
                self._svg_legend.append(SVGElem("circle", cx=x_left + 12, cy=y_current, r=4, fill=plot.color))
                self._svg_legend.append(
                    SVGElem(
                        "text",
                        plot.label,
                        x=x_left + 12 + 12,
                        y=y_current,
                        **{
                            "text-anchor": "start",
                            "dominant-baseline": "middle",
                            "fill": "var(--text)",
                        },
                    )
                )
                y_current += 16

        y_bottom = y_current - 16 + 12

        bg.set_attr("height", int(y_bottom - y_top))

        Session.require().execute(
            _JS_POSITION_LEGEND,
            [self._svg_legend.id, bg.id, self._view.u_max - 24],
        )

    def _xy_to_uv(self, x: float, y: float) -> tuple[float, float]:
        """Convert abstract xy-coordinates to SVG uv-coordinates."""
        u = self._view.u_min + (self._view.u_max - self._view.u_min) * (x - self._view.x_min) / (
            self._view.x_max - self._view.x_min
        )
        v = self._view.v_min + (self._view.v_max - self._view.v_min) * (y - self._view.y_min) / (
            self._view.y_max - self._view.y_min
        )
        return u, v

    def _update_ticks(self) -> None:
        if not hasattr(self, "_svg_ticks"):
            self._svg_ticks = SVGElem(
                "g",
                **{"stroke": "var(--text)", "stroke-width": "1"},
            )
            self.append(self._svg_ticks)

        self._svg_ticks.clear()

        labels = SVGElem("g").style(
            {
                "font-size": "10px",
                "stroke-width": "0",
                "fill": "var(--text)",
            }
        )

        for x, label in self.xticks():
            u, v = self._xy_to_uv(x, self._view.y_min)
            self._svg_ticks.append(SVGElem("line", x1=u, y1=v - 2, x2=u, y2=v + 2))
            labels.append(
                SVGElem(
                    "text",
                    label,
                    x=u,
                    y=v + 4,
                    **{"text-anchor": "middle", "dominant-baseline": "hanging"},
                )
            )

        for y, label in self.yticks():
            u, v = self._xy_to_uv(self._view.x_min, y)
            self._svg_ticks.append(SVGElem("line", x1=u - 2, y1=v, x2=u + 2, y2=v))
            labels.append(
                SVGElem(
                    "text",
                    label,
                    x=u - 4,
                    y=v,
                    **{"text-anchor": "end", "dominant-baseline": "middle"},
                )
            )

        self._svg_ticks.append(labels)
        self._svg_ticks.append(labels)

    def _update_grid(self) -> None:
        if not hasattr(self, "_svg_grid"):
            self._svg_grid = SVGElem("g", **{"stroke": "var(--text)", "stroke-width": "1", "opacity": 0.2})
            self.append(self._svg_grid)

        self._svg_grid.clear()
        if not self.grid:
            return

        for x, _ in self.xticks():
            u, _ = self._xy_to_uv(x, 0)
            self._svg_grid.append(SVGElem("line", x1=u, y1=self._view.v_min, x2=u, y2=self._view.v_max))
        for y, _ in self.yticks():
            _, v = self._xy_to_uv(0, y)
            self._svg_grid.append(SVGElem("line", x1=self._view.u_min, y1=v, x2=self._view.u_max, y2=v))

    def _update_labels(self) -> None:
        if not hasattr(self, "_svg_labels"):
            self._svg_labels = SVGElem("g").style({"fill": "var(--text)"})
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

    def xticks(self) -> Sequence[tuple[float, str]]:
        if self._xticks is not None:
            return self._xticks
        interval = _round_125((self._view.x_max - self._view.x_min) / 10)
        decimals = self._decimals_from_interval(interval)
        x = math.ceil(self._view.x_min / interval) * interval
        ticks = [x]
        while x + interval <= self._view.x_max:
            x += interval
            ticks.append(x)
        return [(x, f"{x:.{decimals}f}") for x in ticks]

    def set_xticks(self, xticks: Sequence[float | tuple[float, str]] | None) -> Self:
        self._xticks: list[tuple[float, str]] | None
        if xticks is not None:
            x_values = [x if isinstance(x, Real) else x[0] for x in xticks]
            decimals = self._decimals_from_interval(min(abs(x2 - x1) for x1, x2 in zip(x_values, x_values[1:])))
            self._xticks = [(x, f"{x:.{decimals}f}") if isinstance(x, Real) else x for x in xticks]  # ty: ignore[invalid-assignment]
        else:
            self._xticks = None
        return self

    def yticks(self) -> Sequence[tuple[float, str]]:
        if self._yticks is not None:
            return self._yticks
        interval = _round_125((self._view.y_max - self._view.y_min) / 10)
        decimals = self._decimals_from_interval(interval)
        y = math.ceil(self._view.y_min / interval) * interval
        ticks = [y]
        while y + interval <= self._view.y_max:
            y += interval
            ticks.append(y)
        return [(y, f"{y:.{decimals}f}") for y in ticks]

    def set_yticks(self, yticks: Sequence[float | tuple[float, str]] | None) -> Self:
        self._yticks: list[tuple[float, str]] | None
        if yticks is not None:
            y_values = [y if isinstance(y, Real) else y[0] for y in yticks]
            decimals = self._decimals_from_interval(min(abs(y2 - y1) for y1, y2 in zip(y_values, y_values[1:])))
            self._yticks = [(y, f"{y:.{decimals}f}") if isinstance(y, Real) else y for y in yticks]  # ty: ignore[invalid-assignment]
        else:
            self._yticks = None
        return self

    def _decimals_from_interval(self, interval: float) -> int:
        """Compute number of decimals required to distinguish numbers that are interval apart."""
        return max(0, math.ceil(-math.log10(interval)))

    def _next_color(self) -> str:
        self._color_counter += 1
        return default_color(self._color_counter - 1)


def _round_125(x: float) -> float:
    """Round to the nearest 1, 2 or 5 times a power of 10."""
    if x == 0:
        return 0
    e = math.floor(math.log10(abs(x)))
    b = abs(x) / 10**e
    r = 1 if b < 1.5 else 2 if b < 3.5 else 5 if b < 7.5 else 1
    e += b >= 7.5
    return math.copysign(r * 10**e, x)


@dataclass
class Plot(ABC):
    """Abstract class containing information for a plot in a :py:class:`Axes` figure.

    Args:
        xs: X-coordinates of data points.
        ys: Y-coordinates of data points.
        color: Color in HTML notation. If ``None``, one of the default colors is used.
        opacity: Opacity value.
        label: Label to be used in the legend.
    """

    xs: Sequence[float]
    ys: Sequence[float]
    color: str | None = None
    label: str | None = None
    opacity: float = 1.0

    @abstractmethod
    def plot(self, frame: SVGElem, xy_to_uv: Callable[[float, float], tuple[float, float]]) -> None:
        """Construct plot elements inside frame.

        Args:
            frame: Element to construct plot elements in.
            xy_to_uv: Function for converting abstract xy-coordinates to
                viewport coordinates.
        """


@dataclass
class Graph(Plot):
    """Graph plot.

    Args:
        xs: X-coordinates of data points.
        ys: Y-coordinates of data points.
        color: Color in HTML notation. If ``None``, one of the default colors is used.
        opacity: Opacity value.
        label: Label to be used in the legend.
    """

    def plot(self, frame: SVGElem, xy_to_uv: Callable[[float, float], tuple[float, float]]):
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
    """Scatter plot.

    Args:
        xs: X-coordinates of data points.
        ys: Y-coordinates of data points.
        color: Color in HTML notation. If ``None``, one of the default colors is used.
        opacity: Opacity value.
        label: Label to be used in the legend.
    """

    def plot(self, frame: SVGElem, xy_to_uv: Callable[[float, float], tuple[float, float]]):
        circles = SVGElem("g", fill=self.color, opacity=str(self.opacity))
        for x, y in zip(self.xs, self.ys):
            u, v = xy_to_uv(x, y)
            circles.append(SVGElem("circle", cx=u, cy=v, r=3))
        frame.append(circles)


@dataclass
class Bar(Plot):
    """Bar plot.

    Args:
        xs: X-coordinates of data points.
        ys: Y-coordinates of data points.
        color: Color in HTML notation. If ``None``, one of the default colors is used.
        opacity: Opacity value.
        label: Label to be used in the legend.
        width: Width of the bars.
    """

    width: float | None = None

    def plot(self, frame: SVGElem, xy_to_uv: Callable[[float, float], tuple[float, float]]):
        bars = SVGElem("g", fill=self.color, opacity=str(self.opacity))

        width = self.width or 0.5 * max(abs(x2 - x1) for x1, x2 in zip(self.xs, self.xs[1:]))

        for x, y in zip(self.xs, self.ys):
            u1, v1 = xy_to_uv(x - width / 2, 0)
            u2, v2 = xy_to_uv(x + width / 2, y)
            y, height = min(v1, v2), abs(v2 - v1)
            bars.append(SVGElem("rect", x=u1, y=y, width=u2 - u1, height=height))

        frame.append(bars)


@dataclass
class FillBetween(Plot):
    """Fill plot.

    Args:
        xs: X-coordinates of data points.
        ys: First set of y-coordinates of data points.
        zs: Second set of y-coordinates of data points.
        color: Color in HTML notation. If ``None``, one of the default colors is used.
        opacity: Opacity value.
        label: Label to be used in the legend.
    """

    def __init__(
        self,
        xs: Sequence[float],
        ys: Sequence[float],
        zs: Sequence[float] | None = None,
        color: str | None = None,
        opacity: float = 1.0,
        label: str | None = None,
    ) -> None:
        super().__init__(xs, ys, color=color, opacity=opacity, label=label)

        self.zs: Sequence[float] = zs if zs is not None else [0.0] * len(xs)

    def plot(self, frame: SVGElem, xy_to_uv: Callable[[float, float], tuple[float, float]]):
        points = []
        for x, y in zip(self.xs, self.ys):
            u, v = xy_to_uv(x, y)
            points.append(f"{u},{v}")
        for x, z in zip(reversed(self.xs), reversed(self.zs)):
            u, v = xy_to_uv(x, z)
            points.append(f"{u},{v}")

        frame.append(
            SVGElem(
                "polyline",
                points=" ".join(points),
                fill=self.color,
                stroke="none",
                opacity=str(self.opacity),
            )
        )
