from __future__ import annotations

from slash import App
from slash.basic.figure import Figure
from slash.basic.progress import Progress
from slash.core import Elem
from slash.html import (
    H1,
    Button,
    Div,
)
from slash.layout import Column

import numpy as np


async def fit(figure: Figure, progress: Progress) -> None:
    # Generate some random points
    a = np.random.uniform(0.0, +0.1)
    b = np.random.uniform(+0.1, +1.0)

    x = np.linspace(0.0, 10.0, 10)
    y = a * x + b + np.random.normal(0.0, 0.05, size=x.shape)

    progress_data = {"value": 0.0}

    from scipy.optimize import minimize

    def loss(ab):
        a, b = ab
        return np.sum((y - a * x - b) ** 2)

    def callback(ab):
        a, b = ab

        figure.clear()
        figure.graph(x, a * x + b)
        figure.scatter(x, y)
        figure.draw()

        progress_data["value"] += 0.01
        progress.set_value(progress_data["value"])

    minimize(
        loss,
        np.array([-1.0, 5.0]),
        method="BFGS",
        options={"gtol": 1e-10, "disp": False},
        callback=callback,
    )

    progress.set_value(1.0)


def home() -> Elem:
    async def async_fit() -> None:
        await fit(figure, progress)

    return Div(
        H1("Fit a line").style({"text-align": "center"}),
        Column(
            figure := Figure(),
            Button("Fit!").onclick(async_fit),
            progress := Progress(),
        ),
    ).style({"max-width": "640px", "margin": "0px auto"})


def main():
    app = App()
    app.add_endpoint("/", home)
    app.run()


if __name__ == "__main__":
    main()
