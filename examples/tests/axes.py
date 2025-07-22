from __future__ import annotations

import math
import random

import numpy as np

from slash.basic.axes import Axes, Bar, Graph, Scatter
from slash.basic.pie import Pie
from slash.core import Elem
from slash.html import H2, Button, Div, Input
from slash.layout import Panel, Row

CENTERED_PANEL = {
    "display": "flex",
    "flex-direction": "column",
    "align-items": "center",
    "margin": "8px 0px",
}


def test_axes() -> Elem:
    return Div(
        H2("Axes"),
        Panel(
            axes := Axes(width=512, height=320)
            .set_title("Some random axes figure")
            .set_xlabel("time (sec)")
            .set_ylabel("amplitude")
            .set_grid(True)
            .set_legend(True)
            .onmount(lambda _: update_axes(axes)),
            Row(
                Button("Update graph").onclick(lambda _: update_axes(axes)),
                Input(
                    placeholder="Enter axes title",
                ).oninput(
                    lambda event: set_axes_title(axes, event.value),
                ),
            ),
        ).style(CENTERED_PANEL),
        Panel(
            pie := Pie(width=512, height=320).onmount(lambda _: update_pie(pie)),
            Button("Update pie chart").onclick(lambda _: update_pie(pie)),
        ).style(CENTERED_PANEL),
        Panel(
            bar := Axes(width=512, height=320).onmount(lambda _: update_bar(bar)),
            Button("Update bar chart").onclick(lambda _: update_bar(bar)),
        ).style(CENTERED_PANEL),
    )


def update_axes(axes: Axes) -> None:
    n = 50
    f = 1 + random.random()
    p = random.random() * 6.28
    xs = [n / 5 for n in range(n + 1)]
    ys = [0.2 + 0.4 * math.sin(f * x + p) for x in xs]

    axes.clear_plots()
    axes.add_plot(Bar(xs, ys, label="bar"))
    axes.add_plot(Graph(xs, ys, label="graph"))
    axes.add_plot(Scatter(xs, ys, label="scatter"))

    axes.set_xlim(-1.0, 11.0)
    axes.set_ylim(-1.0, 1.0)

    axes.render()


def update_pie(pie: Pie) -> None:
    labels = [
        "Apple",
        "Banana",
        "Mango",
        "Strawberry",
        "Orange",
        "Pineapple",
        "Grapes",
        "Watermelon",
        "Blueberry",
        "Peach",
    ]
    values = [random.randint(1, 10) for _ in labels]

    pie.set_title("My Flavourite Fruits").set_radius(112.0).set_gap(32.0).render(labels, values)


def update_bar(bar: Axes) -> None:
    bar.clear_plots()
    bar.set_xlim(0.0, 4.0)
    bar.set_ylim(0.0)

    xs = np.array([1, 2, 3])
    labels = ["2023", "2024", "2025"]

    a, b, c = (
        [random.randint(5, 10), random.randint(5, 10), random.randint(5, 10)],
        [random.randint(5, 10), random.randint(5, 10), random.randint(5, 10)],
        [random.randint(5, 10), random.randint(5, 10), random.randint(5, 10)],
    )

    bar.add_plot(Bar(xs - 0.25, a, width=0.25, label="First"))
    bar.add_plot(Bar(xs, b, width=0.25, label="Second"))
    bar.add_plot(Bar(xs + 0.25, c, width=0.25, label="Third"))
    bar.set_xticks(list(zip(xs, labels)))

    bar.set_legend(True)

    bar.render()


def set_axes_title(axes: Axes, title: str) -> None:
    axes.title = title
    axes.render()
