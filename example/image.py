from __future__ import annotations
from pathlib import Path
import random

from slash import App
from slash.core import Elem, Session
import slash.html as h
from slash.layout import Column

import matplotlib.pyplot as plt
import numpy as np


def update_image(img: h.Img) -> None:
    path = [
        Path("/Users/jessetvogel/Projects/slash/public/img/debug.png"),
        Path("/Users/jessetvogel/Projects/slash/public/img/info.png"),
        Path("/Users/jessetvogel/Projects/slash/public/img/warning.png"),
        Path("/Users/jessetvogel/Projects/slash/public/img/error.png"),
    ][int(4 * random.random())]

    img.src = Session.require().host(path)
    img.style({"height": "64px"})


def generate_graph(image: h.Img) -> None:
    path = Path("./tmp/graph.png")

    f = 1 + random.random() * 10.0

    xs = [x for x in range(10)]
    ys = [np.sin(f * x) for x in xs]

    plt.clf()
    plt.plot(xs, ys)
    plt.savefig(path)

    image.src = Session.require().host(path)
    image.style({"height": "256px"})


def home() -> Elem:
    return Column(
        [
            h.H1("Image demo"),
            image := h.Img(
                "data:image/gif;base64,R0lGODlhAQABAAD/ACwAAAAAAQABAAACADs=",
                alt="This is the alt text.",
            ),
            h.Button("Show an icon!").onclick(lambda _: update_image(image)),
            h.Button("Show a graph!").onclick(lambda _: generate_graph(image)),
        ]
    ).style({"width": "512px", "align-items": "center", "margin": "0px auto"})


def main():
    app = App()
    app.add_endpoint("/", home)
    app.run()


if __name__ == "__main__":
    main()
