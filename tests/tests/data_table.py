from __future__ import annotations

import random

from slash._utils import random_id
from slash.basic._data_table import DataTable
from slash.core import Elem
from slash.html import Code, P, Span
from slash.layout import Column


def test_data() -> Elem:
    return Column(
        P("This page tests the ", Code("DataTable"), " element."),
        P("The following table contains mixed types of data."),
        table_1(),
        P("The following table has custom labels for the columns."),
        table_2(),
    )


def table_1() -> DataTable:
    keys = ["ID", "Name", "Age", "Place", "HTML", "Mixed"]
    data = [
        {
            "ID": n,
            "Name": random.choice(
                ["Peter", "Andrew", "James", "John", "Philip", "Bart", "Thomas", "Matt", "Thad", "Simon", "Judas"]
            )
            + " "
            + random.choice(["Smith", "Brown", "Jones", "Miller", "Davis", "Moore", "Lee", "White", "Green", "Black"]),
            "Age": random.randint(18, 90),
            "Place": random.choice(
                [
                    "Amsterdam",
                    "Brussel",
                    "Paris",
                    "Berlin",
                    "Copenhagen",
                    "Luxembourgh",
                    "Madrid",
                    "Lisabon",
                    "Oslo",
                    "Stockholm",
                    None,
                ]
            ),
            "HTML": random.choice([Elem("b", "<b>"), Elem("i", "<i>"), Code("<code>"), None]),
            "Mixed": random.choice(
                [
                    123,
                    45.6,
                    None,
                    Code("html"),
                ]
            ),
        }
        for n in range(95)
    ]

    return DataTable(keys).set_data(data)


def table_2() -> DataTable:
    keys = ["A", "B", "C", "D", "E", "F"]
    labels = {
        "B": Elem("b", "B"),
        "C": Elem("i", "C"),
        "D": Elem("u", "D"),
        "E": Code("E"),
        "F": Span("F").style({"color": "var(--red)"}),
    }
    data = [
        {
            "A": random_id(),
            "B": random_id(),
            "C": random_id(),
            "D": random_id(),
            "E": random_id(),
            "F": random_id(),
        }
        for _ in range(5)
    ]
    return DataTable(keys).set_data(data).set_labels(labels)
