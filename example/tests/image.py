from __future__ import annotations

import random
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from slash.core import Elem, Session
from slash.html import H2, Button, Div, Img
from slash.layout import Column, Panel, Row


def update_image(img: Img) -> None:
    path = [
        Path("/Users/jessetvogel/Projects/slash/public/img/debug.png"),
        Path("/Users/jessetvogel/Projects/slash/public/img/info.png"),
        Path("/Users/jessetvogel/Projects/slash/public/img/warning.png"),
        Path("/Users/jessetvogel/Projects/slash/public/img/error.png"),
    ][int(4 * random.random())]

    img.src = Session.require().host(path)
    img.style({"height": "64px"})


def generate_graph(image: Img) -> None:
    path = Path("../tmp/graph.png")

    f = 1 + random.random() * 10.0

    xs = [x for x in range(10)]
    ys = [np.sin(f * x) for x in xs]

    plt.clf()
    plt.plot(xs, ys)
    plt.savefig(path)

    image.src = Session.require().host(path)
    image.style({"height": "256px"})


def test_image() -> Elem:
    return Div(
        H2("Image"),
        Panel(
            Column(
                image := Img(
                    "data:image/gif;base64,R0lGODlhAQABAAD/ACwAAAAAAQABAAACADs=",
                    alt="This is the alt text.",
                ),
                Row(
                    Button("Show an icon!").onclick(lambda _: update_image(image)),
                    Button("Show a graph!").onclick(lambda _: generate_graph(image)),
                ),
            ).style({"align-items": "center"})
        ),
    )
