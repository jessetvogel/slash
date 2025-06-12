from __future__ import annotations

from slash.app import App
from slash import html, layout
from slash.core import Elem
from slash.progress import Progress


def move_to_value(progress: Progress, value: float) -> None:
    progress.set_value(value)


def home() -> Elem:
    return layout.Column(
        [
            progress := Progress(),
            layout.Row(
                [
                    html.Button("0%").onclick(lambda _: move_to_value(progress, 0.0)),
                    html.Button("50%").onclick(lambda _: move_to_value(progress, 0.5)),
                    html.Button("100%").onclick(lambda _: move_to_value(progress, 1.0)),
                ]
            ),
        ]
    )


def main():
    app = App()
    app.add_endpoint("/", home)
    app.run()


if __name__ == "__main__":
    main()
