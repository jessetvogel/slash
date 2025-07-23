from slash.core import Elem
from slash.html import Button, Div, P
from slash.layout import Column, Panel, Row


def test_dom() -> Elem:
    state = {"count": 0}
    label = Div().style({"padding": "8px"})

    def set_counter(value: int) -> None:
        state["count"] = value
        label.text = f"Counter: {value}"

    set_counter(0)

    return Div(
        P("This page tests various methods for DOM manipulation."),
        Column(
            Panel(
                label,
                Row(
                    Button("+1").onclick(lambda: set_counter(state["count"] + 1)),
                    Button("-1").onclick(lambda: set_counter(state["count"] - 1)),
                    Button("Reset").onclick(lambda: set_counter(0)),
                ).style({"justify-content": "center"}),
            ).style({"text-align": "center"}),
            Panel(
                P("Move the black dot"),
                row := Row(
                    black := circle("var(--black)"),
                    circle("var(--red)"),
                    circle("var(--yellow)"),
                    circle("var(--green)"),
                    circle("var(--blue)"),
                    circle("var(--purple)"),
                ).style({"gap": "8px", "justify-content": "center", "margin-bottom": "16px"}),
                Row(
                    Button("<").onclick(lambda: row.insert(max(0, row.children.index(black) - 1), black)),
                    Button(">").onclick(lambda: row.insert(row.children.index(black) + 1, black)),
                ).style({"justify-content": "center"}),
            ).style({"text-align": "center"}),
        ).style({"gap": "8px"}),
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
