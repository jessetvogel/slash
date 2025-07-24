from slash.core import Elem
from slash.html import Button, Code, Dialog, Div, P, Span
from slash.layout import Column, Row


def test_dialog() -> Elem:
    return Div(
        P("This page tests the ", Code("Dialog"), " element."),
        Div(
            Row(
                Button("Dialog.show()").onclick(lambda: dialog.show()).style({"font-family": "monospace"}),
                Button("Dialog.show_modal()").onclick(lambda: dialog.show_modal()).style({"font-family": "monospace"}),
            ).style({"gap": "8px"}),
            dialog := Dialog(
                Column(
                    Span("This is a dialog element!"),
                    Button("Close").onclick(lambda: dialog.close()),
                ).style({"gap": "16px"})
            ),
        ),
    )
