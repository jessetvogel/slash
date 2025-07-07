from __future__ import annotations

import math
import random

from slash import App
from slash.basic import Figure
from slash.basic.figure import Bar, Graph, Scatter
from slash.core import Elem
from slash.html import H1, Button, Input
from slash.layout import Column, Panel, Row


def update_figure(figure: Figure) -> None:
    n = 50
    f = 1 + random.random()
    p = random.random() * 6.28
    xs = [n / 5 for n in range(n + 1)]
    ys = [0.2 + 0.4 * math.sin(f * x + p) for x in xs]

    figure.clear_plots()
    figure.add_plot(Bar(xs, ys, color="var(--green)", label="bar"))
    figure.add_plot(Graph(xs, ys, color="var(--secondary-color)", label="graph"))
    figure.add_plot(Scatter(xs, ys, color="var(--primary-color)", label="scatter"))

    figure.set_xlim(-1.0, 11.0)
    figure.set_ylim(-1.0, 1.0)

    figure.render()


def set_figure_title(figure: Figure, title: str) -> None:
    figure.title = title
    figure.render()


def home() -> Elem:
    return Column(
        H1("Figure demo"),
        Panel(
            figure := Figure(width=512, height=320)
            .set_title("Some random figure")
            .set_xlabel("time (sec)")
            .set_ylabel("amplitude")
            .set_grid(True)
            .set_legend(True)
        ),
        Button("Click me!").onclick(lambda _: update_figure(figure)),
        Row(
            Input(
                placeholder="Enter figure title",
            ).oninput(
                lambda event: set_figure_title(figure, event.value),
            )
        ),
    ).style({"width": "512px", "align-items": "center", "margin": "0px auto"})


def main():
    app = App()
    app.add_endpoint("/", home)
    app.run()


if __name__ == "__main__":
    main()
