from __future__ import annotations

from slash.basic import Icon
from slash.core import Elem
from slash.html import Code, Div, P, Span
from slash.layout import Panel


def test_icons() -> Elem:
    return Div(
        P("This page tests the ", Code("Icon"), " element."),
        Panel(
            Div(
                [
                    [
                        Div(Icon(icon)).style({"width": "24px", "height": "24px", "background-color": "var(--gray)"}),
                        Icon(icon),
                        Span(icon.capitalize()),
                    ]
                    for icon in [
                        "info",
                        "warning",
                        "error",
                        "debug",
                        "success",
                        "loading",
                        "help",
                        "moon",
                        "sun",
                        "trash",
                    ]
                ]
            ).style(
                {
                    "display": "grid",
                    "grid-template-columns": "repeat(3, max-content)",
                    "justify-content": "center",
                    "align-items": "center",
                    "gap": "8px",
                }
            )
        ),
    )
