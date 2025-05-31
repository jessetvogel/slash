from __future__ import annotations

import random
from slash.app import App
import slash.core as e
from slash.message import Message


def home() -> e.Elem:
    state = {"counter": 0, "textarea": ""}

    label = e.Span("Counter: ")
    counter = e.Span("0")

    def increment_counter(_: e.ClickEvent):
        state["counter"] += 1
        counter.text = str(state["counter"])

    def reset_counter(_: e.ClickEvent):
        state["counter"] = 0
        counter.text = "0"

    button = e.Button("+1", onclick=increment_counter)
    reset = e.Button("Reset", onclick=reset_counter)

    reversed_text = e.Span("Reversed text: ")

    def oninput_callback(event: e.InputEvent):
        reversed_text.text = f"Reversed text: {''.join(reversed(event.value))}"

    def trigger_error(event: e.ClickEvent):
        event.target.page.broadcast(Message.error("An error occured!"))

    def trigger_info(event: e.ClickEvent):
        event.target.page.broadcast(Message.info("Info message!"))

    def trigger_debug(event: e.ClickEvent):
        event.target.page.broadcast(Message.debug("Debug message!"))

    def onchange_textarea(event: e.ChangeEvent):
        state["textarea"] = event.value

    def onclick_execute_function(event: e.ClickEvent):
        textarea.page.broadcast(Message.function("tmp", [], str(state["textarea"])))
        textarea.page.broadcast(Message.execute("tmp", []))

    return e.Div(
        [
            e.Div(
                [square(n) for n in range(1, 11)],
                style={"display": "flex", "gap": "16px", "flex-wrap": "wrap"},
            ),
            e.Div([label, counter, button, reset]),
            e.Div(
                [
                    e.Input(oninput=oninput_callback),
                    reversed_text,
                ]
            ),
            e.Div(
                [
                    e.Button("ℹ️ Trigger info", onclick=trigger_info),
                    e.Button("🧪 Trigger debug", onclick=trigger_debug),
                    e.Button("🚨 Trigger error", onclick=trigger_error),
                ]
            ),
            e.Div(
                [
                    textarea := e.Textarea(
                        "alert('Hello world!');", onchange=onchange_textarea
                    ),
                    e.Button("Execute as function", onclick=onclick_execute_function),
                ]
            ),
        ]
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


def onclick_square(event: e.ClickEvent) -> None:
    event.target.style = {"background-color": random_hex_color()}


def random_hex_color() -> str:
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))


def main():
    app = App()
    app.add_endpoint("/", home)
    app.run()


if __name__ == "__main__":
    main()
