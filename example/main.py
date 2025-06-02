from __future__ import annotations

import random
from slash.app import App
import slash.core as e
from slash.jsfunction import JSFunction
from slash.layout import Column


def home() -> e.Elem:
    state = {"counter": 0, "textarea": ""}

    label = e.Span("Counter: ")
    counter = e.Span("0")

    def increment_counter(_: e.ClickEvent):
        state["counter"] += 1
        counter.text = str(state["counter"])

    def decrement_counter(_: e.ClickEvent):
        state["counter"] -= 1
        counter.text = str(state["counter"])

    def reset_counter(_: e.ClickEvent):
        state["counter"] = 0
        counter.text = "0"

    button_increment = e.Button("+1", onclick=increment_counter)
    button_decrement = e.Button("-1", onclick=decrement_counter)
    reset = e.Button("Reset", onclick=reset_counter)

    reversed_text = e.Span("Reversed text: ")

    def oninput_callback(event: e.InputEvent):
        reversed_text.text = f"Reversed text: {''.join(reversed(event.value))}"

    def trigger_info(event: e.ClickEvent):
        event.target.client.log("info", "Example info message")

    def trigger_debug(event: e.ClickEvent):
        event.target.client.log("debug", "Example debug message")

    def trigger_warning(event: e.ClickEvent):
        event.target.client.log("warning", "Example warning message")

    def trigger_error(event: e.ClickEvent):
        event.target.client.log("error", "Example error message")

    def onchange_textarea(event: e.ChangeEvent):
        state["textarea"] = event.value

    def onclick_execute_function(event: e.ClickEvent):
        jsfunction = JSFunction([], str(state["textarea"]))
        textarea.client.execute(jsfunction, [])

    return e.Div(
        [
            e.Div(
                [square(n) for n in range(1, 5)],
                style={"display": "flex", "gap": "16px", "flex-wrap": "wrap"},
            ),
            e.Div([label, counter, button_decrement, button_increment, reset]),
            e.Div(
                [
                    e.Input(placeholder="Type something...", oninput=oninput_callback),
                    reversed_text,
                ]
            ),
            e.Div(
                [
                    e.Button("Trigger info", onclick=trigger_info),
                    e.Button("Trigger debug", onclick=trigger_debug),
                    e.Button("Trigger warning", onclick=trigger_warning),
                    e.Button("Trigger error", onclick=trigger_error),
                ]
            ),
            e.Div(
                [
                    textarea := e.Textarea(
                        placeholder="Write some JS here..", onchange=onchange_textarea
                    ),
                    e.Button("Execute as function", onclick=onclick_execute_function),
                ]
            ),
            Column(
                [
                    e.H2("<input> elements"),
                    e.Input("button"),
                    e.Input("checkbox"),
                    e.Input("color"),
                    e.Input("date"),
                    e.Input("datetime-local"),
                    e.Input("email"),
                    e.Input("file"),
                    e.Input("hidden"),
                    e.Input("month"),
                    e.Input("number"),
                    e.Input("password"),
                    e.Input("radio"),
                    e.Input("range"),
                    e.Input("reset"),
                    e.Input("search"),
                    e.Input("submit"),
                    e.Input("tel"),
                    e.Input("text"),
                    e.Input("time"),
                    e.Input("url"),
                    e.Input("week"),
                ],
                style={"width": "512px"},
            ),
            e.Div(
                [
                    e.H2("header elements"),
                    e.H1("<h1> element"),
                    e.H2("<h2> element"),
                    e.H3("<h3> element"),
                    e.H4("<h4> element"),
                    e.H5("<h5> element"),
                    e.H6("<h6> element"),
                ]
            ),
            e.Div(
                [
                    e.H2("Lorem ipsum"),
                    e.P(
                        " Lorem ipsum dolor sit amet, consectetur adipiscing elit. Morbi a vehicula enim, sed malesuada purus. Aliquam erat volutpat. Pellentesque vel sagittis erat. Suspendisse pellentesque dictum justo quis semper. Suspendisse lobortis nisl suscipit enim dapibus interdum. Proin vel vestibulum justo. Maecenas in tellus ac leo blandit mattis. Fusce quis feugiat ipsum. Proin pellentesque ut nunc sed accumsan."
                    ),
                    e.H2("Duis ac tempus eros"),
                    e.P(
                        "Duis ac tempus eros, nec feugiat felis. Proin efficitur augue faucibus sapien condimentum interdum. Etiam a nibh ac ante scelerisque sodales. Sed eu orci aliquet, sodales dolor in, vestibulum diam. Ut sed est libero. Morbi erat elit, iaculis et scelerisque ultrices, eleifend non dui. Mauris id magna eget dolor posuere porttitor id at leo. Quisque porttitor sem quis sem dignissim ultrices. Fusce at tellus nec urna posuere suscipit interdum at nulla. Ut nec metus tristique, dictum dui non, scelerisque lacus. Nam consequat dolor non sodales molestie. Suspendisse laoreet dolor arcu, non pellentesque lacus vehicula quis."
                    ),
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
