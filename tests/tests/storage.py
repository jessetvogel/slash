from slash.core import Elem, Session
from slash.html import Button, Code, Input, P, Span
from slash.layout import Column, Row


def update_span(span: Span) -> None:
    session = Session.require()
    value = session.get_data("test_storage") or "<none>"
    span.set_text("Currently stored value: " + value).style({"padding": "8px"})


def update_storage(value: str, span: Span) -> None:
    session = Session.require()
    session.set_data("test_storage", value)
    update_span(span)


def test_storage() -> Elem:
    return Column(
        P(
            "This page tests the ",
            Code("Session.set_data"),
            " and ",
            Code("Session.get_data"),
            " methods to set and get values in localstorage.",
        ),
        P(span := Span().onmount(lambda: update_span(span))),
        Row(
            input := Input(placeholder="Enter new value here"),
            Button("Store").onclick(lambda: update_storage(input.value, span)),
        ).style({"gap": "16px"}),
    )
