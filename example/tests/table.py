from __future__ import annotations

from slash._utils import random_id
from slash.basic import Table
from slash.core import Elem
from slash.html import H2, Button
from slash.layout import Column


def update_table(table: Table) -> None:
    table.set_data(
        [[random_id(), random_id(), random_id(), random_id()] for _ in range(10)]
    )


def test_table() -> Elem:
    return Column(
        H2("Table"),
        table := Table(),
        Button("Update table").onclick(lambda _: update_table(table)),
    )
