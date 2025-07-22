from slash.core import Elem, Session
from slash.html import H2, Div, Table, Td, Tr


def test_session() -> Elem:
    session = Session.require()
    return Div(
        H2("Session"),
        Table(
            Tr(Td("Session.path").style({"font-family": "monospace"}), Td(session.path)),
            *[
                Tr(
                    Td(f"Session.query['{name}']").style({"font-family": "monospace"}),
                    Td(value),
                )
                for name, value in session.query.items()
            ],
        ),
    )
