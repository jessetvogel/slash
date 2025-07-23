from __future__ import annotations

import json

from slash import App
from slash.core import Elem, PopStateEvent, Session
from slash.html import H2, Button, Div, Span
from slash.layout import Column, Panel, Row


def back() -> Button:
    return Button("< Back").onclick(lambda: Session.require().history.back())


def forward() -> Button:
    return Button("Forward >").onclick(lambda: Session.require().history.forward())


def page(animal: str, food: str) -> Elem:
    session = Session.require()
    session.history.onpopstate(lambda event: handle_popstate(event))

    state = {"animal": animal, "food": food}

    def handle_popstate(event: PopStateEvent) -> None:
        session.log(
            "debug",
            (f"Received <code>popstate</code> event with state:<pre><code>{json.dumps(event.state)}</code></pre>"),
            format="html",
        )
        if isinstance(event.state, dict):
            set_state("animal", event.state["animal"])
            set_state("food", event.state["food"])
        else:
            set_state("animal", "none")
            set_state("food", "none")

    def set_state(key: str, value: str) -> None:
        state[key] = value
        span_animal.set_text(state["animal"])
        span_food.set_text(state["food"])

    def update_state(key: str, value: str) -> None:
        set_state(key, value)
        session.history.push(state, f"/page/{state['animal']}/{state['food']}")

    return Column(
        H2("History"),
        Panel(
            Div("Favorite animal: ", span_animal := Span(animal)),
            Div("Favorite food: ", span_food := Span(food)),
        ),
        Span("Navigate through history"),
        Row(back(), forward()),
        Span("Choose your new favorite animal"),
        Row(
            Button("Koala 🐨").onclick(lambda: update_state("animal", "koala")),
            Button("Orangutan 🦧").onclick(lambda: update_state("animal", "orangutan")),
            Button("Zebra 🦓").onclick(lambda: update_state("animal", "zebra")),
        ).style({"align-items": "center"}),
        Span("Choose your new favorite food"),
        Row(
            Button("Burger 🍔").onclick(lambda: update_state("food", "burger")),
            Button("Sandwich 🥪").onclick(lambda: update_state("food", "sandwich")),
            Button("Fries 🍟").onclick(lambda: update_state("food", "fries")),
        ).style({"align-items": "center"}),
    ).style({"padding": "8px", "gap": "8px", "align-items": "baseline"})


def main():
    app = App()
    app.add_route("/", lambda: page("none", "none"))
    app.add_route(r"/page/(\w+)/(\w+)", page)
    app.run()


if __name__ == "__main__":
    main()
