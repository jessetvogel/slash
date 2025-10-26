from slash.core import Elem, Session
from slash.html import A, Button, Code, P
from slash.layout import Column, Row


def test_log() -> Elem:
    return Column(
        P("This page tests the log messages. Click one of the following buttons to trigger a log message."),
        Row(
            Button("Info").onclick(
                lambda: Session.require().log(
                    "Example info message",
                    level="info",
                )
            ),
            Button("Debug").onclick(
                lambda: Session.require().log(
                    "Example debug message",
                    level="debug",
                )
            ),
            Button("Warning").onclick(
                lambda: Session.require().log(
                    "Example warning message",
                    level="warning",
                )
            ),
            Button("Error").onclick(
                lambda: Session.require().log(
                    "Example error message",
                    level="error",
                )
            ),
        ).style({"gap": "8px"}),
        P("Trigger one of the following buttons to trigger a log message with details."),
        Row(
            Button("Info").onclick(
                lambda: Session.require().log(
                    "Info message",
                    level="info",
                    details="Some extra details",
                )
            ),
            Button("Debug").onclick(
                lambda: Session.require().log(
                    "Debug message",
                    level="debug",
                    details=Code("details_in_code"),
                )
            ),
            Button("Warning").onclick(
                lambda: Session.require().log(
                    "Warning message",
                    level="warning",
                    details=Button("Interactive details").onclick(lambda: Session.require().log("Log-ception!")),
                )
            ),
            Button("Error").onclick(
                lambda: Session.require().log(
                    "Error message",
                    level="error",
                    details=A("Click here to get a free coupon!"),
                )
            ),
        ).style({"gap": "8px"}),
    )
