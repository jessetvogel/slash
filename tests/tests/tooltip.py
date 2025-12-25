from slash.basic import Tooltip
from slash.core import Elem, Session
from slash.html import Button, Code, Dialog, Div, P, Span
from slash.layout import Column, Row


def test_tooltip() -> Elem:
    return Column(
        P(
            "This page tests the ",
            Code("Tooltip"),
            " element. ",
            "Hover over the circles below to show a tooltip.",
        ),
        Row(
            red := circle("red"),
            Tooltip("This is a red circle.", target=red),
            blue := circle("blue"),
            Tooltip("This is not a red circle.", target=blue),
            yellow := circle("yellow"),
            Tooltip(
                "This circle is ",
                Span("yellow").style({"color": "var(--yellow)", "font-style": "italic", "font-weight": "bold"}),
                ".",
                target=yellow,
            ),
            green := circle("green").style({"border-radius": "2px"}),
            Tooltip(
                "This circle is not a circle.",
                target=green,
            ),
            button_1 := Button("Button")
            .onclick(lambda: Session.require().log("I'm not angry, just disappointed..", level="warning"))
            .style({"border-radius": "100%", "width": "96px", "height": "96px"}),
            Tooltip("Don't click this button!", target=button_1),
            button_2 := Button("💬")
            .onclick(lambda: dialog.show_modal())
            .style({"border-radius": "4px", "width": "48px", "height": "48px"}),
            Tooltip("Please click me!", target=button_2),
        ).style({"gap": "16px", "align-items": "center"}),
        dialog := Dialog(
            Div(
                close_top := Button("🏃‍♂️🚪").onclick(lambda: dialog.close()),
                Tooltip(
                    "Close dialog window",
                    target=close_top,
                ),
                close_bottom := Button("🚪🏃‍♂️‍➡️").onclick(lambda: dialog.close()),
                Tooltip(
                    "Also close dialog window",
                    target=close_bottom,
                ),
            ).style(
                {
                    "display": "flex",
                    "flex-direction": "column",
                    "justify-content": "space-between",
                    "align-items": "center",
                    "width": "256px",
                    "height": "256px",
                }
            )
        ),
    )


def circle(color: str) -> Div:
    return Div().style(
        {
            "width": "32px",
            "height": "32px",
            "border-radius": "32px",
            "background-color": f"var(--{color})",
        }
    )
