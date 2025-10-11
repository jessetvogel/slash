from slash.basic._tabs import Tabs
from slash.core import Elem
from slash.html import Code, Div, P


def test_tabs() -> Elem:
    def set_tab(value: str) -> None:
        if value == "Tab 1":
            content.set_text("This is the first tab!")
        elif value == "Tab 2":
            content.set_text("Welcome to the second tab!")
        elif value == "Tab 3":
            content.set_text("You made it to the third tab!")

    return Div(
        P("This page tests the ", Code("Tabs"), " element."),
        tabs := Tabs(
            ["Tab 1", "Tab 2", "Tab 3"],
        ).onchange(lambda event: set_tab(event.value)),
        content := Div().style({"padding": "8px"}).onmount(lambda: set_tab(tabs.value)),
    )
