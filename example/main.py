from __future__ import annotations

import random
from slash.core import Elem, Session
from slash import App
from slash.events import ChangeEvent, ClickEvent, InputEvent
from slash.html import H1, H2, H3, H4, H5, H6, P, Button, Div, Input, Span, Textarea
from slash.js import JSFunction
from slash.layout import Column


def home() -> Elem:
    state_counter = {"count": 0}
    state_textarea = {"text": ""}

    label = Span("Counter: ")
    counter = Span("0")

    def increment_counter(_: ClickEvent):
        state_counter["count"] += 1
        counter.text = str(state_counter["count"])

    def decrement_counter(_: ClickEvent):
        state_counter["count"] -= 1
        counter.text = str(state_counter["count"])

    def reset_counter(_: ClickEvent):
        state_counter["count"] = 0
        counter.text = "0"

    button_increment = Button("+1").onclick(increment_counter)
    button_decrement = Button("-1").onclick(decrement_counter)
    reset = Button("Reset").onclick(reset_counter)

    reversed_text = Span("Reversed text: ")

    def oninput_callback(event: InputEvent):
        reversed_text.text = f"Reversed text: {''.join(reversed(event.value))}"

    def trigger_info(_: ClickEvent):
        Session.require().log("info", "Example info message")

    def trigger_debug(_: ClickEvent):
        Session.require().log("debug", "Example debug message")

    def trigger_warning(_: ClickEvent):
        Session.require().log("warning", "Example warning message")

    def trigger_error(_: ClickEvent):
        Session.require().log("error", "Example error message")

    def onchange_textarea(event: ChangeEvent):
        state_textarea["text"] = event.value

    def onclick_execute_function(event: ClickEvent):
        jsfunction = JSFunction([], state_textarea["text"])
        Session.require().execute(jsfunction, [])

    return Div(
        [
            Div([square(n) for n in range(1, 5)]).style(
                {"display": "flex", "gap": "16px", "flex-wrap": "wrap"},
            ),
            Div([label, counter, button_decrement, button_increment, reset]),
            Div(
                [
                    Input(placeholder="Type something...").oninput(oninput_callback),
                    reversed_text,
                ]
            ),
            Div(
                [
                    Button("Trigger info").onclick(trigger_info),
                    Button("Trigger debug").onclick(trigger_debug),
                    Button("Trigger warning").onclick(trigger_warning),
                    Button("Trigger error").onclick(trigger_error),
                ]
            ),
            Div(
                [
                    Textarea(placeholder="Write some JS her.").onchange(
                        onchange_textarea
                    ),
                    Button("Execute as function").onclick(onclick_execute_function),
                ]
            ),
            Column(
                [
                    H2("<input> elements"),
                    Input("button"),
                    Input("checkbox"),
                    Input("color"),
                    Input("date"),
                    Input("datetime-local"),
                    Input("email"),
                    Input("file"),
                    Input("hidden"),
                    Input("month"),
                    Input("number"),
                    Input("password"),
                    Input("radio"),
                    Input("range"),
                    Input("reset"),
                    Input("search"),
                    Input("submit"),
                    Input("tel"),
                    Input("text"),
                    Input("time"),
                    Input("url"),
                    Input("week"),
                ]
            ).style(
                {"width": "512px"},
            ),
            Div(
                [
                    H2("header elements"),
                    H1("<h1> element"),
                    H2("<h2> element"),
                    H3("<h3> element"),
                    H4("<h4> element"),
                    H5("<h5> element"),
                    H6("<h6> element"),
                ]
            ),
            Div(
                [
                    H2("Lorem ipsum"),
                    P(
                        " Lorem ipsum dolor sit amet, consectetur adipiscing elit. Morbi a vehicula enim, sed malesuada purus. Aliquam erat volutpat. Pellentesque vel sagittis erat. Suspendisse pellentesque dictum justo quis semper. Suspendisse lobortis nisl suscipit enim dapibus interdum. Proin vel vestibulum justo. Maecenas in tellus ac leo blandit mattis. Fusce quis feugiat ipsum. Proin pellentesque ut nunc sed accumsan."
                    ),
                    H2("Duis ac tempus eros"),
                    P(
                        "Duis ac tempus eros, nec feugiat felis. Proin efficitur augue faucibus sapien condimentum interdum. Etiam a nibh ac ante scelerisque sodales. Sed eu orci aliquet, sodales dolor in, vestibulum diam. Ut sed est libero. Morbi erat elit, iaculis et scelerisque ultrices, eleifend non dui. Mauris id magna eget dolor posuere porttitor id at leo. Quisque porttitor sem quis sem dignissim ultrices. Fusce at tellus nec urna posuere suscipit interdum at nulla. Ut nec metus tristique, dictum dui non, scelerisque lacus. Nam consequat dolor non sodales molesti Suspendisse laoreet dolor arcu, non pellentesque lacus vehicula quis."
                    ),
                    Elem(
                        "pre",
                        """def fibonacci(n):
    a = 0
    b = 1
    
    # Check if n is less than 0
    if n < 0:
        print("Incorrect input")
        
    # Check if n is equal to 0
    elif n == 0:
        return 0
      
    # Check if n is equal to 1
    elif n == 1:
        return b
    else:
        for i in range(1, n):
            c = a + b
            a = b
            b = c
        return b""",
                    ),
                ]
            ),
        ]
    )


def square(n: int) -> Elem:
    return (
        Div(f"Square {n}")
        .style(
            {
                "width": "100px",
                "height": "100px",
                "border": "1px solid black",
                "border-radius": "8px",
                "display": "flex",
                "align-items": "center",
                "justify-content": "center",
            },
        )
        .onclick(onclick_square)
    )


def onclick_square(event: ClickEvent) -> None:
    event.target.style({"background-color": random_hex_color()})


def random_hex_color() -> str:
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))


def main():
    app = App()
    app.add_endpoint("/", home)
    app.run()


if __name__ == "__main__":
    main()
