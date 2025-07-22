from slash.core import Elem
from slash.html import H1, Div


def page_404() -> Elem:
    return Div(H1("Page not found!"), Div("Oops, this page does not exist..")).style(
        {"margin": "auto", "max-width": "512px", "text-align": "center"}
    )
