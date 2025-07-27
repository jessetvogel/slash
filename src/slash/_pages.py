from slash.core import Elem, Session
from slash.html import H1, Button, Div
from slash.layout import Column


def page_404() -> Elem:
    return Column(
        H1("Page not found!"),
        Div("Oops, this page does not exist.."),
        Button("👈 Back to homepage").onclick(lambda: Session.require().set_location("/")),
    ).style({"margin": "auto", "max-width": "512px", "align-items": "center", "gap": "8px"})
