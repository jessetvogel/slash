from __future__ import annotations

from slash.app import App
import slash.core as e
from slash.image import Image
from slash.layout import Column


def update_image(image: Image) -> None:
    pass


def home() -> e.Elem:
    return Column(
        [
            e.H1("Image demo"),
            image := Image(),
            e.Button("Click me!", onclick=lambda _: update_image(image)),
        ],
        style={"width": "512px", "align-items": "center", "margin": "0px auto"},
    )


def main():
    app = App()
    app.add_endpoint("/", home)
    app.run()


if __name__ == "__main__":
    main()
