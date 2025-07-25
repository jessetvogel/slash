from slash.core import Elem, Session
from slash.html import H3, Code, Div, Input, P
from slash.layout import Column


def test_session() -> Elem:
    session = Session.require()

    return Div(
        P("This page tests various properties of the ", Code("Session"), " object."),
        Div(
            H3("Session properties"),
            Column(
                Div(Code("Session.id"), " equals ", Code(session.id)),
                Div(Code("Session.location.url"), " equals ", Code(session.location.url)),
                Div(Code("Session.location.protocol"), " equals ", Code(session.location.scheme)),
                Div(Code("Session.location.host"), " equals ", Code(session.location.host)),
                Div(Code("Session.location.hostname"), " equals ", Code(str(session.location.hostname))),
                Div(Code("Session.location.port"), " equals ", Code(str(session.location.port))),
                Div(Code("Session.location.path"), " equals ", Code(session.location.path)),
                Div(Code("Session.location.query"), " equals ", Code(str(session.location.query))),
                Div(Code("Session.location.fragment"), " equals ", Code(session.location.fragment)),
            ).style({"gap": "8px"}),
            H3("Document title"),
            Input(placeholder="Type new document title..").oninput(lambda event: session.set_title(event.value)),
        ),
    )
