from slash.core import Elem, Session
from slash.html import H3, Button, Div, P, Table, Td, Tr
from slash.layout import Column, Row

COLORS = [
    "red",
    "orange",
    "yellow",
    "green",
    "teal",
    "blue",
    "indigo",
    "purple",
    "pink",
    "aubergine",
]


def test_colors() -> Elem:
    return Column(
        P("This page tests the colors and themes."),
        H3("Set theme"),
        Row(
            Button("dark").onclick(lambda: Session.require().set_theme("dark")),
            Button("light").onclick(lambda: Session.require().set_theme("light")),
        ).style({"gap": "8px", "align-items": "center"}),
        H3("Table of colors"),
        Table([Tr(Td(color), Td(circle(f"var(--{color})")).style({"width": "32px"})) for color in COLORS]).style(
            {"width": "256px"}
        ),
    ).style({"align-items": "center"})


def circle(color: str) -> None:
    return Div().style(
        {
            "background-color": color,
            "border-radius": "32px",
            "width": "32px",
            "height": "32px",
        }
    )
