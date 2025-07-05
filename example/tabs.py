from __future__ import annotations

from slash import App
from slash.basic import Figure, Markdown, Tabs
from slash.core import Elem
from slash.events import MountEvent
from slash.html import H2, Div, P
from slash.layout import Column


def tab_1() -> Elem:
    return Div(
        H2("Lorem ipsum"),
        P(
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec sem eros, fringilla et nisl sed, scelerisque finibus sem. Maecenas et imperdiet nisl, bibendum sodales sem. Vivamus diam ligula, interdum vitae quam auctor, porttitor euismod arcu. Nulla pretium ultricies dolor quis porttitor. Nullam vestibulum quam a feugiat egestas. Duis non vehicula justo, ut commodo orci. Praesent imperdiet elit a nibh rutrum scelerisque. Donec et ligula elementum neque euismod tempor. Donec lacinia, nulla quis egestas aliquam, lacus nisi blandit lectus, vel cursus eros turpis ut neque. In quam turpis, interdum eu velit a, lobortis suscipit ipsum. Morbi ullamcorper massa id est dignissim, vel auctor tellus aliquet. Cras vulputate finibus nisl, non lacinia tellus sagittis in. Aenean et accumsan dolor."
        ),
    )


def tab_2() -> Elem:
    figure = Figure()

    def tmp(_: MountEvent) -> None:
        figure.graph([0, 1, 2, 3], [1, 0, 1, 0])
        figure.draw()

    figure.onmount(tmp)
    return figure


def tab_3() -> Elem:
    return Markdown(
        """
# Header

## Subheader

## Subsubheader

This is written in **Markdown**.

Consider the following list of items:

- Item 1
- Item 2
- Item 3

Consider the following numbered list of items:

1. Item A
2. Item B
3. Item C

Some text can be *italic* and some text can be **bold**.

Some text can be <span style="color: blue">blue</span> and some can be <span style="color: red">red</span>.

There can be [hyperlinks](https://jessetvogel.nl) and there can be `code`.

    // Even a block of code is possible.

> Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec sem eros, fringilla et nisl sed, scelerisque finibus sem. Maecenas et imperdiet nisl, bibendum sodales sem. Vivamus diam ligula, interdum vitae quam auctor, porttitor euismod arcu.

This is an image: ![slash icon](/img/favicon.png)

---

That was a horizontal line.

Btw, does <https://www.jessetvogel.nl> also work?

"""
    )


def home() -> Elem:
    content = Div()

    def set_tab(value: str) -> None:
        if value == "Latin":
            content.clear()
            content.append(tab_1())

        elif value == "Figure":
            content.clear()
            content.append(tab_2())

        elif value == "Markdown":
            content.clear()
            content.append(tab_3())

    return Column(
        tabs := Tabs(
            ["Latin", "Figure", "Markdown"],
        ).onchange(lambda event: set_tab(event.value)),
        content.onmount(lambda _: set_tab(tabs.value)),
    )


def main():
    app = App()
    app.add_endpoint("/", home)
    app.run()


if __name__ == "__main__":
    main()
