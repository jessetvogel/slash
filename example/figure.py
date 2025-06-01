from __future__ import annotations
import math
import random

from slash.app import App
import slash.core as e
from slash.figure import Figure
from slash.layout import Column


def update_graph(graph: Figure) -> None:
    n = 100
    f = 1 + random.random()
    p = random.random() * 6.28
    xs = [n / 10 for n in range(n + 1)]
    ys = [0.5 + 0.4 * math.sin(f * x + p) for x in xs]
    graph.plot(
        xs,
        ys,
        xlabel="time (sec)",
        ylabel="amplitude",
        grid=True,
        title="Amplitude vs time",
        color="red",
    )


def home() -> e.Elem:
    return Column(
        [
            e.H1("Graph demo"),
            graph := Figure(),
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
