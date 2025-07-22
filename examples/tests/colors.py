from slash.core import Elem, Session
from slash.html import H2, Button, Div
from slash.layout import Column, Row


def test_colors() -> Elem:
    return Column(
        H2("Colors"),
        Row(
            [
                circle(f"var(--{color})")
                for color in [
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
            ]
            + [
                Button("dark").style({"margin-left": "auto"}).onclick(lambda: Session.require().set_theme("dark")),
                Button("light").onclick(lambda: Session.require().set_theme("light")),
            ]
        ).style({"gap": "8px", "align-items": "center"}),
    )


def circle(color: str) -> None:
    return Div().style(
        {
            "background-color": color,
            "border-radius": "32px",
            "width": "32px",
            "height": "32px",
        }
    )
