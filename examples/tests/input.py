from slash.core import Elem
from slash.html import H2, Div, Input, P
from slash.layout import Panel


def test_input() -> Elem:
    return Div(
        H2("Input"),
        Panel(
            P("The text written in the left input element should appear backwards in the right input element."),
            Input(placeholder="Write here!").oninput(lambda event: out.set_value("".join(reversed(event.value)))),
            out := Input(),
        ).style({"margin": "8px 0px"}),
        Panel(
            Input("button"),
            Input("checkbox"),
            Input("color"),
            Input("date"),
            Input("datetime-local"),
            Input("email"),
            Input("file"),
            Input("hidden"),
            Input("month"),
            Input("number"),
            Input("password"),
            Input("radio"),
            Input("range"),
            Input("reset"),
            Input("search"),
            Input("submit"),
            Input("tel"),
            Input("text"),
            Input("time"),
            Input("url"),
            Input("week"),
        ),
    )
