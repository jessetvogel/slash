from __future__ import annotations

from slash.app import App
from slash import html, layout
from slash.core import Elem


def home() -> Elem:
    return layout.Column(
        [
            html.H2("Dialog demo"),
            html.Div(
                [
                    html.Button("Dialog.show()").onclick(lambda _: dialog.show()),
                    html.Button("Dialog.show_modal()").onclick(
                        lambda _: dialog.show_modal()
                    ),
                    dialog := html.Dialog(
                        layout.Column(
                            [
                                html.Span("This is a dialog element!"),
                                html.Button("Close").onclick(lambda _: dialog.close()),
                            ],
                            style={"gap": "16px"},
                        )
                    ),
                ]
            ),
        ],
        style={"width": "512px", "align-items": "center", "margin": "0px auto"},
    )


def main():
    app = App()
    app.add_endpoint("/", home)
    app.run()


if __name__ == "__main__":
    main()
