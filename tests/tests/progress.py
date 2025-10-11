from slash.basic._progress import Progress
from slash.core import Elem
from slash.html import Button, Code, P
from slash.layout import Column, Row


def test_progress() -> Elem:
    return Column(
        P("This page tests the ", Code("Progress"), " element."),
        progress := Progress(),
        Row(
            Button("0%").onclick(lambda: progress.set_value(0.0)),
            Button("25%").onclick(lambda: progress.set_value(0.25)),
            Button("50%").onclick(lambda: progress.set_value(0.5)),
            Button("75%").onclick(lambda: progress.set_value(0.75)),
            Button("100%").onclick(lambda: progress.set_value(1.0)),
        ).style({"justify-content": "center", "gap": "16px"}),
    ).style({"gap": "16px"})
