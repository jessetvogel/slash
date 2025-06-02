from __future__ import annotations

from slash.app import App
import slash.core as e
from slash.layout import Column
from slash.table import Table


def update_table(table: Table) -> None:
    table.data(
        [
            [e.random_id(), e.random_id(), e.random_id(), e.random_id()]
            for _ in range(10)
        ]
    )


def home() -> e.Elem:
    return Column(
        [
            e.H1("Table demo"),
            table := Table(),
            e.Button("Click me!", onclick=lambda _: update_table(table)),
        ],
        style={"width": "512px", "align-items": "center", "margin": "0px auto"},
    )


def main():
    app = App()
    app.add_endpoint("/", home)
    app.run()


if __name__ == "__main__":
    main()
