from __future__ import annotations

import random
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from slash._server import PATH_PUBLIC
from slash.core import Elem, Session
from slash.html import Button, Code, Div, Img, P
from slash.layout import Column, Panel, Row


def update_image(img: Img) -> None:
    path = [
        Path(PATH_PUBLIC / "img/debug.png"),
        Path(PATH_PUBLIC / "img/info.png"),
        Path(PATH_PUBLIC / "img/warning.png"),
        Path(PATH_PUBLIC / "img/error.png"),
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
        P("This page tests the ", Code("Img"), " element."),
        Panel(
            Column(
                image := Img(
                    src="data:image/gif;base64,R0lGODlhAQABAAD/ACwAAAAAAQABAAACADs=",
                    alt="This is the alt text.",
                ).style({"background-color": "var(--black)"}),
                Row(
                    Button("Show an icon").onclick(lambda _: update_image(image)),
                    Button("Generate a graph").onclick(lambda _: generate_graph(image)),
                ).style({"gap": "8px"}),
            ).style({"align-items": "center", "gap": "8px"})
        ),
    )
