from slash.core import Elem, Session
from slash.html import Button, Div, P
from slash.layout import Row


def test_log() -> Elem:
    return Div(
        P("This page tests the log messages. Click one of the following buttons to trigger a log message."),
        Row(
            Button("Info").onclick(lambda: Session.require().log("info", "Example info message")),
            Button("Debug").onclick(lambda: Session.require().log("debug", "Example debug message")),
            Button("Warning").onclick(lambda: Session.require().log("warning", "Example warning message")),
            Button("Error").onclick(lambda: Session.require().log("error", "Example error message")),
        ),
    )
