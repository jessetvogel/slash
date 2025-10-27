from __future__ import annotations

import json

from slash.core import Elem, PopStateEvent, Session
from slash.html import Button, Code, Div, P, Pre, Span
from slash.layout import Column, Panel, Row


def back() -> Button:
    return Button("< Back").onclick(lambda: Session.require().history.back())


def forward() -> Button:
    return Button("Forward >").onclick(lambda: Session.require().history.forward())


def test_history() -> Elem:
    session = Session.require()
    session.history.onpopstate(lambda event: handle_popstate(event))

    state = {"animal": session.location.query.get("animal", "none"), "food": session.location.query.get("food", "none")}

    def handle_popstate(event: PopStateEvent) -> None:
        session.log(
            "Event popstate",
            level="debug",
            details=Pre(Code(json.dumps(event.state))),
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
        session.history.push(state, session.location.path + f"?animal={state['animal']}&food={state['food']}")

    return Column(
        P(
            "This page tests the ",
            Code("Session.history"),
            " object.",
            "While changing the animal or food, the page should not reload, ",
            "but the history state (and URL) should be updated. ",
            "Going forward and backward through history should again not reload the page, "
            "except when leaving the page. ",
            "When the ",
            Code("popstate"),
            " event is fired, a message should appear with the new state.",
        ),
        Panel(
            Div("Favorite animal: ", span_animal := Span(state["animal"])),
            Div("Favorite food: ", span_food := Span(state["food"])),
        ),
        Span("Navigate through history"),
        Row(back(), forward()).style({"gap": "8px"}),
        Span("Choose your new favorite animal"),
        Row(
            Button("Koala 🐨").onclick(lambda: update_state("animal", "koala")),
            Button("Orangutan 🦧").onclick(lambda: update_state("animal", "orangutan")),
            Button("Zebra 🦓").onclick(lambda: update_state("animal", "zebra")),
        ).style({"align-items": "center", "gap": "8px"}),
        Span("Choose your new favorite food"),
        Row(
            Button("Burger 🍔").onclick(lambda: update_state("food", "burger")),
            Button("Sandwich 🥪").onclick(lambda: update_state("food", "sandwich")),
            Button("Fries 🍟").onclick(lambda: update_state("food", "fries")),
        ).style({"align-items": "center", "gap": "8px"}),
    ).style({"padding": "8px", "gap": "8px", "align-items": "baseline"})
