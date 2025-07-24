from slash.basic.progress import Progress
from slash.core import Elem
from slash.html import Button, Div
from slash.layout import Column, Row


def test_progress() -> Elem:
    return Div(
        Column(
            progress := Progress(),
            Row(
                Button("0%").onclick(lambda: progress.set_value(0.0)),
                Button("25%").onclick(lambda: progress.set_value(0.25)),
                Button("50%").onclick(lambda: progress.set_value(0.5)),
                Button("75%").onclick(lambda: progress.set_value(0.75)),
                Button("100%").onclick(lambda: progress.set_value(1.0)),
            ).style({"justify-content": "center", "gap": "8px"}),
        ).style({"gap": "8px"}),
    )
