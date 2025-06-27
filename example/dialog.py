from __future__ import annotations

from slash import App
from slash.core import Elem
from slash.html import H2, Button, Dialog, Div, Span
from slash.layout import Column


def home() -> Elem:
    return Column(
        [
            H2("Dialog demo"),
            Div(
                [
                    Button("Dialog.show()").onclick(lambda _: dialog.show()),
                    Button("Dialog.show_modal()").onclick(
                        lambda _: dialog.show_modal()
                    ),
                    dialog := Dialog(
                        Column(
                            [
                                Span("This is a dialog element!"),
                                Button("Close").onclick(lambda _: dialog.close()),
                            ],
                        ).style({"gap": "16px"})
                    ),
                ]
            ),
        ],
    ).style({"width": "512px", "align-items": "center", "margin": "0px auto"})


def main():
    app = App()
    app.add_endpoint("/", home)
    app.run()


if __name__ == "__main__":
    main()
