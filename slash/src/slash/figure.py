import random
from typing import Any

from slash.core import Elem, HTML
from slash.message import Message


class Figure(Elem):
    def __init__(
        self, *, title: str = "", xlabel: str = "", ylabel: str = "", grid: bool = False
    ):
        self._canvas = HTML("canvas", width=512, height=384)
        super().__init__(children=[self._canvas])
        self._title = title
        self._xlabel = xlabel
        self._ylabel = ylabel
        self._grid = grid
        self._js_figure_id = self.id + "_js_figure"

    def _create_js_figure(self) -> None:
        options = {
            "title": self._title,
            "xlabel": self._xlabel,
            "ylabel": self._ylabel,
            "grid": self._grid,
        }

        self.page.reply(
            Message.execute(
                FUNCTION_CREATE[0], [self._canvas.id, options], self._js_figure_id
            )
        )

    @property
    def tag(self) -> str:
        return "div"

    def attrs(self) -> dict[str, Any]:
        return {"class": "slash-figure"}

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, value: str) -> None:
        self._title = value

    @property
    def xlabel(self) -> str:
        return self._xlabel

    @xlabel.setter
    def xlabel(self, value: str) -> None:
        self._xlabel = value

    @property
    def ylabel(self) -> str:
        return self._ylabel

    @ylabel.setter
    def ylabel(self, value: str) -> None:
        self._ylabel = value

    @property
    def grid(self) -> bool:
        return self._grid

    @grid.setter
    def grid(self, value: bool) -> None:
        self._grid = value

    def clear(self) -> None:
        self.page.reply(Message.execute(FUNCTION_CLEAR[0], [self._js_figure_id]))

    def draw(self) -> None:
        self.page.reply(Message.execute(FUNCTION_DRAW[0], [self._js_figure_id]))

    def graph(
        self,
        xs: list[float],
        ys: list[float],
        *,
        color: str | None = None,
    ) -> None:
        options: dict[str, Any] = {"color": color or random_hex_color()}
        self.page.reply(
            Message.execute(
                FUNCTION_GRAPH[0], [self._js_figure_id, list(zip(xs, ys)), options]
            )
        )

    def scatter(
        self,
        xs: list[float],
        ys: list[float],
        *,
        color: str | None = None,
    ) -> None:
        options: dict[str, Any] = {"color": color or random_hex_color()}
        self.page.reply(
            Message.execute(
                FUNCTION_SCATTER[0],
                [self._js_figure_id, list(zip(xs, ys)), options],
            )
        )

    def mount(self) -> None:
        self.page.require_function(*FUNCTION_CREATE)
        self.page.require_function(*FUNCTION_SCATTER)
        self.page.require_function(*FUNCTION_GRAPH)
        self.page.require_function(*FUNCTION_CLEAR)
        self.page.require_function(*FUNCTION_DRAW)

        self._create_js_figure()


def random_hex_color() -> str:
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))


FUNCTION_CREATE = (
    "Figure_create",
    ["id", "options"],
    "return new Figure(document.getElementById(id), options)",
)

FUNCTION_SCATTER = (
    "Figure_scatter",
    ["id", "pts", "options"],
    """
    const figure = Slash.value(id);
    const scatter = new Scatter(pts, options);
    figure.plot(scatter);
    """,
)

FUNCTION_GRAPH = (
    "Figure_graph",
    ["id", "pts", "options"],
    """
    const figure = Slash.value(id);
    const graph = new Graph(pts, options);
    figure.plot(graph);
    """,
)

FUNCTION_CLEAR = (
    "Figure_clear",
    ["id"],
    "Slash.value(id).clear()",
)

FUNCTION_DRAW = (
    "Figure_draw",
    ["id"],
    "Slash.value(id).draw()",
)
