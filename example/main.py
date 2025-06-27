from __future__ import annotations

import random
from slash.app import App
from slash.core import ChangeEvent, ClickEvent, Elem, InputEvent, Session
import slash.html as h
from slash.js import JSFunction
from slash.layout import Column


def home() -> Elem:
    state_counter = {"count": 0}
    state_textarea = {"text": ""}

    label = h.Span("Counter: ")
    counter = h.Span("0")

    def increment_counter(_: ClickEvent):
        state_counter["count"] += 1
        counter.text = str(state_counter["count"])

    def decrement_counter(_: ClickEvent):
        state_counter["count"] -= 1
        counter.text = str(state_counter["count"])

    def reset_counter(_: ClickEvent):
        state_counter["count"] = 0
        counter.text = "0"

    button_increment = h.Button("+1").onclick(increment_counter)
    button_decrement = h.Button("-1").onclick(decrement_counter)
    reset = h.Button("Reset").onclick(reset_counter)

    reversed_text = h.Span("Reversed text: ")

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

    return h.Div(
        [
            h.Div([square(n) for n in range(1, 5)]).style(
                {"display": "flex", "gap": "16px", "flex-wrap": "wrap"},
            ),
            h.Div([label, counter, button_decrement, button_increment, reset]),
            h.Div(
                [
                    h.Input(placeholder="Type something...").oninput(oninput_callback),
                    reversed_text,
                ]
            ),
            h.Div(
                [
                    h.Button("Trigger info").onclick(trigger_info),
                    h.Button("Trigger debug").onclick(trigger_debug),
                    h.Button("Trigger warning").onclick(trigger_warning),
                    h.Button("Trigger error").onclick(trigger_error),
                ]
            ),
            h.Div(
                [
                    h.Textarea(placeholder="Write some JS her.").onchange(
                        onchange_textarea
                    ),
                    h.Button("Execute as function").onclick(onclick_execute_function),
                ]
            ),
            Column(
                [
                    h.H2("<input> elements"),
                    h.Input("button"),
                    h.Input("checkbox"),
                    h.Input("color"),
                    h.Input("date"),
                    h.Input("datetime-local"),
                    h.Input("email"),
                    h.Input("file"),
                    h.Input("hidden"),
                    h.Input("month"),
                    h.Input("number"),
                    h.Input("password"),
                    h.Input("radio"),
                    h.Input("range"),
                    h.Input("reset"),
                    h.Input("search"),
                    h.Input("submit"),
                    h.Input("tel"),
                    h.Input("text"),
                    h.Input("time"),
                    h.Input("url"),
                    h.Input("week"),
                ]
            ).style(
                {"width": "512px"},
            ),
            h.Div(
                [
                    h.H2("header elements"),
                    h.H1("<h1> element"),
                    h.H2("<h2> element"),
                    h.H3("<h3> element"),
                    h.H4("<h4> element"),
                    h.H5("<h5> element"),
                    h.H6("<h6> element"),
                ]
            ),
            h.Div(
                [
                    h.H2("Lorem ipsum"),
                    h.P(
                        " Lorem ipsum dolor sit amet, consectetur adipiscing elit. Morbi a vehicula enim, sed malesuada purus. Aliquam erat volutpat. Pellentesque vel sagittis erat. Suspendisse pellentesque dictum justo quis semper. Suspendisse lobortis nisl suscipit enim dapibus interdum. Proin vel vestibulum justo. Maecenas in tellus ac leo blandit mattis. Fusce quis feugiat ipsum. Proin pellentesque ut nunc sed accumsan."
                    ),
                    h.H2("Duis ac tempus eros"),
                    h.P(
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
        h.Div(f"Square {n}")
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
