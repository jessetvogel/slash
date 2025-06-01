import random
from typing import Any

from slash.core import Elem, HTML
from slash.message import Message


class Figure(Elem):
    def __init__(self):
        self._canvas = HTML("canvas", width=512, height=384)
        super().__init__(children=[self._canvas])

    @property
    def tag(self) -> str:
        return "div"

    def attrs(self) -> dict[str, Any]:
        return {"class": "slash-figure"}

    def plot(
        self,
        xs: list[float],
        ys: list[float],
        *,
        grid: bool = False,
        xlabel: str | None = None,
        ylabel: str | None = None,
        title: str | None = None,
        color: str | None = None,
    ) -> None:
        self.page.broadcast(
            Message.function(
                "graph_plot",
                ["id", "pts", "options"],
                """
const figure = new Figure(document.getElementById(id));
figure.options = options;
const graph = new Graph(pts, options);
figure.graphs.push(graph);
figure.draw();
""",
            )
        )

        # set options
        options: dict[str, Any] = {}
        if grid:
            options["grid"] = True
        if title:
            options["title"] = title
        if xlabel:
            options["xlabel"] = xlabel
        if xlabel:
            options["ylabel"] = ylabel
        if color:
            options["color"] = random_hex_color()

        self.page.broadcast(
            Message.execute("graph_plot", [self._canvas.id, list(zip(xs, ys)), options])
        )


def random_hex_color() -> str:
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))
