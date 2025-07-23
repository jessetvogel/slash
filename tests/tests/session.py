from slash.core import Elem, Session
from slash.html import Div, Table, Td, Tr


def test_session() -> Elem:
    session = Session.require()
    return Div(
        Table(
            Tr(Td("Session.path:").style({"font-family": "monospace", "width": "128px"}), Td(session.path)),
            *[
                Tr(
                    Td(f"Session.query['{name}']:").style({"font-family": "monospace"}),
                    Td(value),
                )
                for name, value in session.query.items()
            ],
        )
    )
