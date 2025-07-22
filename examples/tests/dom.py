from slash.core import Elem
from slash.html import H2, H3, Button, Div, Span
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
        Panel(
            H3("Move the black dot"),
            row := Row(
                black := circle("var(--black)"),
                circle("var(--red)"),
                circle("var(--yellow)"),
                circle("var(--green)"),
                circle("var(--blue)"),
                circle("var(--purple)"),
            ).style({"gap": "8px"}),
            Row(
                Button("<").onclick(lambda: row.insert(max(0, row.children.index(black) - 1), black)),
                Button(">").onclick(lambda: row.insert(row.children.index(black) + 1, black)),
            ),
        ),
    )


def circle(color: str) -> None:
    return Div().style(
        {
            "background-color": color,
            "border-radius": "32px",
            "width": "32px",
            "height": "32px",
        }
    )
