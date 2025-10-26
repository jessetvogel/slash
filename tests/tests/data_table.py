from __future__ import annotations

import random

from slash.basic._data_table import DataTable
from slash.core import Elem
from slash.html import Code, P
from slash.layout import Column


def test_data() -> Elem:
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

    return Column(P("This page tests the ", Code("DataTable"), " element."), DataTable(keys).set_data(data))
