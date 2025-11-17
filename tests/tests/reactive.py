from typing import Any

from slash.core import Elem
from slash.html import Code, Div, Input, P, Span
from slash.reactive import Computed, Effect, Signal


def input_for_signal(type: str, signal: Signal[Any]) -> Input:
    return (
        Input(type, value=str(signal.get()))
        .style({"width": "64px", "text-align": "center"})
        .oninput(lambda event: signal.set(int(event.value) if event.value else 0))
    )


def span_for_readable(readable: Signal[Any] | Computed[Any]) -> Span:
    span = Span()
    Effect(lambda: span.set_text(str(readable())))
    return span


def test_reactive() -> Elem:
    cows = Signal(2)
    pigs = Signal(3)
    cats = Signal(5)
    animals = Computed(lambda: cows() + pigs() + cats())

    cow_emojis = Computed(lambda: "🐮" * cows())
    pig_emojis = Computed(lambda: "🐷" * pigs())
    cat_emojis = Computed(lambda: "🐱" * cats())
    all_emojis = Computed(lambda: cow_emojis() + pig_emojis() + cat_emojis())

    return Div(
        P("This page tests the ", Code("slash.reactive"), " functionality."),
        P(
            "John 👨‍🌾 has a farm 🚜. The farm has ",
            input_for_signal("number", cows),
            " cows and ",
            input_for_signal("number", pigs),
            " pigs and ",
            input_for_signal("number", cats),
            " cats. ",
            "In total, John has ",
            span_for_readable(animals).style({"font-weight": "bold"}),
            " animals.",
        ),
        P("John's farm looks as follows. "),
        P(span_for_readable(all_emojis).style({"font-size": "1.5rem"})),
    )
