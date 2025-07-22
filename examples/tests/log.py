from slash.core import Elem, Session
from slash.html import H2, Button, Div


def test_log() -> Elem:
    return Div(
        H2("Logging"),
        Button("Trigger info").onclick(lambda: Session.require().log("info", "Example info message")),
        Button("Trigger debug").onclick(lambda: Session.require().log("debug", "Example debug message")),
        Button("Trigger warning").onclick(lambda: Session.require().log("warning", "Example warning message")),
        Button("Trigger error").onclick(lambda: Session.require().log("error", "Example error message")),
    )
