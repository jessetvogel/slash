from slash.core import Elem
from slash.html import H2, Button, Div, Span
from slash.layout import Panel, Row


def test_dom() -> Elem:
    state = {"count": 0}
    label = Span().style({"padding": "8px"})

    def set_counter(value: int) -> None:
        state["count"] = value
        label.text = f"Counter: {value}"

    set_counter(0)

    return Div(
        H2("DOM"),
        Panel(
            label,
            Row(
                Button("+1").onclick(lambda: set_counter(state["count"] + 1)),
                Button("-1").onclick(lambda: set_counter(state["count"] - 1)),
                Button("Reset").onclick(lambda: set_counter(0)),
            ),
        ),
    )
