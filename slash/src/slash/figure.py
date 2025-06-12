import random
from typing import Any, Self

from slash.core import Elem
from slash.js import JSFunction

# class FigureOption:
#   TODO


class Figure(Elem):
    def __init__(
        self, *, title: str = "", xlabel: str = "", ylabel: str = "", grid: bool = False
    ):
        self._canvas = Elem("canvas", width=512, height=384)
        super().__init__("div", children=[self._canvas], **{"class": "slash-figure"})  # type: ignore[arg-type]
        self._title = title
        self._xlabel = xlabel
        self._ylabel = ylabel
        self._grid = grid
        self._js_figure_id = self.id + "_js_figure"
        self.onmount(self._create_js_figure)

    def _create_js_figure(self) -> None:
        options = {
            "title": self._title,
            "xlabel": self._xlabel,
            "ylabel": self._ylabel,
            "grid": self._grid,
        }

        self.client.execute(
            FUNCTION_CREATE, [self._canvas.id, options], self._js_figure_id
        )

    def _update_options(self, options: dict[str, Any]) -> None:
        self.client.execute(FUNCTION_SET, [self._js_figure_id, options])

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, value: str) -> None:
        self._title = value
        self._update_options({"title": value})

    @property
    def xlabel(self) -> str:
        return self._xlabel

    @xlabel.setter
    def xlabel(self, value: str) -> None:
        self._xlabel = value
        self._update_options({"xlabel": value})

    @property
    def ylabel(self) -> str:
        return self._ylabel

    @ylabel.setter
    def ylabel(self, value: str) -> None:
        self._ylabel = value
        self._update_options({"ylabel": value})

    @property
    def grid(self) -> bool:
        return self._grid

    @grid.setter
    def grid(self, value: bool) -> None:
        self._grid = value
        self._update_options({"grid": value})

    def clear(self) -> None:
        self.client.execute(FUNCTION_CLEAR, [self._js_figure_id])

    def draw(self) -> Self:
        self.client.execute(FUNCTION_DRAW, [self._js_figure_id])
        return self

    def graph(
        self,
        xs: list[float],
        ys: list[float],
        *,
        color: str | None = None,
    ) -> Self:
        options: dict[str, Any] = {"color": color or random_hex_color()}
        self.client.execute(
            FUNCTION_GRAPH, [self._js_figure_id, list(zip(xs, ys)), options]
        )
        return self

    def scatter(
        self,
        xs: list[float],
        ys: list[float],
        *,
        color: str | None = None,
    ) -> Self:
        options: dict[str, Any] = {"color": color or random_hex_color()}
        self.client.execute(
            FUNCTION_SCATTER,
            [self._js_figure_id, list(zip(xs, ys)), options],
        )
        return self


FUNCTION_CREATE = JSFunction(
    ["id", "options"],
    "return new Figure(document.getElementById(id), options)",
)

FUNCTION_SCATTER = JSFunction(
    ["id", "pts", "options"],
    """
    const figure = Slash.value(id);
    const scatter = new Scatter(pts, options);
    figure.plot(scatter);
    """,
)

FUNCTION_GRAPH = JSFunction(
    ["id", "pts", "options"],
    """
    const figure = Slash.value(id);
    const graph = new Graph(pts, options);
    figure.plot(graph);
    """,
)

FUNCTION_CLEAR = JSFunction(
    ["id"],
    "Slash.value(id).clear()",
)

FUNCTION_SET = JSFunction(
    ["id", "options"],
    """
    const figure = Slash.value(id);
    for (const key in options)
        figure.options[key] = options[key];
    """,
)

FUNCTION_DRAW = JSFunction(
    ["id"],
    "Slash.value(id).draw()",
)


def random_hex_color() -> str:
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))
