from slash.core import Elem
from slash.html import H2, Button, Dialog, Div, Span
from slash.layout import Column


def test_dialog() -> Elem:
    return Div(
        H2("Dialog"),
        Div(
            Button("Dialog.show()").onclick(lambda: dialog.show()),
            Button("Dialog.show_modal()").onclick(lambda: dialog.show_modal()),
            dialog := Dialog(
                Column(
                    Span("This is a dialog element!"),
                    Button("Close").onclick(lambda: dialog.close()),
                ).style({"gap": "16px"})
            ),
        ),
    )
