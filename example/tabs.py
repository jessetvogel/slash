from __future__ import annotations

from slash import html, layout
from slash.app import App
from slash.core import Elem
from slash.figure import Figure
from slash.tabs import Tabs


def tab_1() -> Elem:
    return html.Div(
        [
            html.H2("Lorem ipsum"),
            html.P(
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec sem eros, fringilla et nisl sed, scelerisque finibus sem. Maecenas et imperdiet nisl, bibendum sodales sem. Vivamus diam ligula, interdum vitae quam auctor, porttitor euismod arcu. Nulla pretium ultricies dolor quis porttitor. Nullam vestibulum quam a feugiat egestas. Duis non vehicula justo, ut commodo orci. Praesent imperdiet elit a nibh rutrum scelerisque. Donec et ligula elementum neque euismod tempor. Donec lacinia, nulla quis egestas aliquam, lacus nisi blandit lectus, vel cursus eros turpis ut neque. In quam turpis, interdum eu velit a, lobortis suscipit ipsum. Morbi ullamcorper massa id est dignissim, vel auctor tellus aliquet. Cras vulputate finibus nisl, non lacinia tellus sagittis in. Aenean et accumsan dolor."
            ),
        ]
    )


def tab_2() -> Elem:
    figure = Figure()

    def tmp(figure: Figure) -> None:
        Figure.onmount(figure)
        figure.graph([0, 1, 2, 3], [1, 0, 1, 0])
        figure.draw()

    figure.onmount = lambda: tmp(figure)
    return figure


def tab_3() -> Elem:
    return html.Span("Some more text.")


def set_tab(content: Elem, value: str) -> None:
    if value == "Tab 1":
        content.clear()
        content.append(tab_1())

    elif value == "Tab 2":
        content.clear()
        content.append(tab_2())

    elif value == "Tab 3":
        content.clear()
        content.append(tab_3())


def home() -> Elem:
    content = html.Div()
    return layout.Column(
        [
            Tabs(
                ["Tab 1", "Tab 2", "Tab 3"],
                onchange=lambda event: set_tab(content, event.value),
            ),
            content,
        ]
    )


def main():
    app = App()
    app.add_endpoint("/", home)
    app.run()


if __name__ == "__main__":
    main()
