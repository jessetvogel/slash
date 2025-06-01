from __future__ import annotations
import math
import random

from slash.app import App
import slash.core as e
from slash.figure import Figure
from slash.layout import Column


def update_graph(figure: Figure) -> None:
    n = 50
    f = 1 + random.random()
    p = random.random() * 6.28
    xs = [n / 5 for n in range(n + 1)]
    ys = [0.5 + 0.4 * math.sin(f * x + p) for x in xs]

    figure.clear()
    figure.graph(xs, ys, color="--secondary-color")
    figure.scatter(xs, ys, color="--primary-color")
    figure.draw()


def home() -> e.Elem:
    return Column(
        [
            e.H1("Graph demo"),
            graph := Figure(
                title="Some random graph",
                xlabel="time (sec)",
                ylabel="amplitude",
                grid=True,
            ),
            e.Button("Click me!", onclick=lambda _: update_graph(graph)),
        ],
        style={"width": "512px", "align-items": "center", "margin": "0px auto"},
    )


def main():
    app = App()
    app.add_endpoint("/", home)
    app.run()


if __name__ == "__main__":
    main()
