from __future__ import annotations
import math
import random

from slash import App
from slash.basic.figure import Figure, Graph, Scatter
from slash.core import Elem
from slash.html import H2
from slash.layout import Column, Panel


def home() -> Elem:
    f = random.random() * 10

    xs = [i / 50 for i in range(50)]
    ys = [math.sin(f * x) ** 2 for x in xs]

    ys_noise = [y + (random.random() - 0.5) * 0.1 for y in ys]

    return Column(
        H2("SVG demo"),
        Panel(
            Figure(width=640, height=320)
            .set_title("Example figure")
            .set_xlabel("x-label")
            .set_ylabel("y-label")
            .set_legend(True)
            .set_grid(True)
            .add_plot(Graph(xs, ys, label="graph plot"))
            .add_plot(Scatter(xs, ys_noise, label="scatter plot"))
            .render()
        ),
    ).style({"width": "512px", "align-items": "center", "margin": "0px auto"})


def main():
    app = App()
    app.add_endpoint("/", home)
    app.run()


if __name__ == "__main__":
    main()
