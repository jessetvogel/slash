from __future__ import annotations
from pathlib import Path
import random

from slash.app import App
import slash.core as e
from slash.image import Image
from slash.layout import Column

import matplotlib.pyplot as plt
import numpy as np


def update_image(image: Image) -> None:
    path = [
        Path("/Users/jessetvogel/Projects/slash/public/img/debug.png"),
        Path("/Users/jessetvogel/Projects/slash/public/img/info.png"),
        Path("/Users/jessetvogel/Projects/slash/public/img/warning.png"),
        Path("/Users/jessetvogel/Projects/slash/public/img/error.png"),
    ][int(4 * random.random())]

    image.src = image.client.host(path)
    image.style = {"height": "64px"}


def generate_graph(image: Image) -> None:
    path = Path("./tmp/graph.png")

    f = 1 + random.random() * 10.0

    xs = [x for x in range(10)]
    ys = [np.sin(f * x) for x in xs]

    plt.clf()
    plt.plot(xs, ys)
    plt.savefig(path)

    image.src = image.client.host(path)
    image.style = {"height": "256px"}


def home() -> e.Elem:
    return Column(
        [
            e.H1("Image demo"),
            image := Image(
                "data:image/gif;base64,R0lGODlhAQABAAD/ACwAAAAAAQABAAACADs=",
                alt="This is the alt text.",
            ),
            e.Button("Click me!", onclick=lambda _: update_image(image)),
            e.Button("Generate graph!", onclick=lambda _: generate_graph(image)),
        ],
        style={"width": "512px", "align-items": "center", "margin": "0px auto"},
    )


def main():
    app = App()
    app.add_endpoint("/", home)
    app.run()


if __name__ == "__main__":
    main()
