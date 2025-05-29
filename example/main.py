import random
from slash.app import App
import slash.core as e


def home() -> e.Elem:
    return e.Div(
        [square(n) for n in range(1, 11)],
        style={"display": "flex", "gap": "16px", "flex-wrap": "wrap"},
    )


def square(n: int) -> e.Elem:
    return e.Div(
        f"Square {n}",
        style={
            "width": "100px",
            "height": "100px",
            "border": "1px solid black",
            "border-radius": "8px",
            "display": "flex",
            "align-items": "center",
            "justify-content": "center",
        },
        onclick=onclick_square,
    )


def onclick_square(event: e.MouseEvent) -> None:
    event.target.style = {"background-color": random_hex_color()}


def random_hex_color() -> str:
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))


def main():
    app = App()
    app.add_endpoint("/", home)
    app.run()


if __name__ == "__main__":
    main()
