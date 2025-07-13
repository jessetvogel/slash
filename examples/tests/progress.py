from slash.basic.progress import Progress
from slash.core import Elem
from slash.html import H2, Button, Div
from slash.layout import Column, Panel, Row


def test_progress() -> Elem:
    return Div(
        H2("Progress"),
        Panel(
            Column(
                progress := Progress(),
                Row(
                    Button("0%").onclick(lambda: progress.set_value(0.0)),
                    Button("50%").onclick(lambda: progress.set_value(0.5)),
                    Button("100%").onclick(lambda: progress.set_value(1.0)),
                ).style({"justify-content": "space-between"}),
            )
        ),
    )
