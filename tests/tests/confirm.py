from slash.basic._confirm import confirm
from slash.core import Elem
from slash.html import Button, Code, Div, P
from slash.layout import Column


def test_confirm() -> Elem:
    async def delete_circle() -> None:
        if await confirm(
            "Are you sure you want to delete the circle?",
            ok_text="Yes, definitely",
            cancel_text="No, rather not",
        ):
            circle.unmount()
            button.disabled = True

    return Column(
        P(
            "This page tests the ",
            Code("confirm"),
            " method. ",
            "Click the button to show a confirmation dialog.",
        ),
        circle := Div().style(
            {
                "width": "64px",
                "height": "64px",
                "background-color": "var(--red)",
                "border-radius": "64px",
            }
        ),
        button := Button("🗑️ Delete circle").onclick(delete_circle),
    ).style({"align-items": "center", "gap": "16px"})
