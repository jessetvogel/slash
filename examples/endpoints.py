from __future__ import annotations

from slash import App
from slash.core import Elem
from slash.html import H2, A, Span
from slash.layout import Column


def home() -> Elem:
    return Column(
        H2("Animal pages"),
        A("👉 /animal/chicken", href="/animal/chicken"),
        A("👉 /animal/cow", href="/animal/cow"),
        A("👉 /animal/pig", href="/animal/pig"),
    ).style({"padding": "8px", "gap": "8px"})


def animal(animal: str) -> Elem:
    emojis = {"cow": "🐮", "chicken": "🐔", "pig": "🐷"}
    return Column(
        H2(f"Welcome to the page about {animal}s {emojis[animal]}"),
        Span(f"TODO: add information about {animal}s"),
    ).style({"padding": "8px", "gap": "8px"})


def date(day: str, month: str, year: str) -> Elem:
    return Column(
        H2(f"Date {day}-{month}-{year}"),
        Span("..."),
    ).style({"padding": "8px", "gap": "8px"})


def main():
    app = App()
    app.add_route("/", home)
    app.add_route(r"/animal/(\w+)", animal)
    app.add_route(r"/date/(\d+)/(\d+)/(\d+)", date)
    app.run()


if __name__ == "__main__":
    main()
