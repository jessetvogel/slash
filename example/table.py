from __future__ import annotations

from slash import App
from slash._utils import random_id
from slash.basic import Table
from slash.core import Elem
from slash.html import H1, Button
from slash.layout import Column


def update_table(table: Table) -> None:
    table.data(
        [[random_id(), random_id(), random_id(), random_id()] for _ in range(10)]
    )


def home() -> Elem:
    return Column(
        H1("Table demo"),
        table := Table(),
        Button("Click me!").onclick(lambda _: update_table(table)),
    ).style({"width": "512px", "align-items": "center", "margin": "0px auto"})


def main():
    app = App()
    app.add_endpoint("/", home)
    app.run()


if __name__ == "__main__":
    main()
