from slash.core import Elem
from slash.html import Code, Div, Input, P, Textarea


def test_input() -> Elem:
    return Div(
        P(
            "This page tests the ",
            Code("oninput"),
            " event handlers. ",
            "The text written in the left input element should appear backwards in the right input element.",
        ),
        Input(placeholder="Write here!").oninput(lambda event: out_1.set_value("".join(reversed(event.value)))),
        out_1 := Input().style({"margin-left": "8px"}),
        P("The text written in the left textarea should appear in upper case in the right textarea element."),
        Textarea(placeholder="Write here!").oninput(lambda event: out_2.set_value(event.value.upper())),
        out_2 := Textarea().style({"margin-left": "8px"}),
    )
